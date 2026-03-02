from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document import Document
from app.services.document import document_service
from app.services.llm import llm_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    # Validate file type
    allowed_types = [".pdf", ".txt", ".docx"]
    suffix = "." + file.filename.split(".")[-1].lower()
    if suffix not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Use: {allowed_types}")

    # Save file
    content = await file.read()
    filepath = await document_service.save_file(file.filename, content)

    # Extract text
    text = await document_service.extract_text(filepath)

    # Create database record (user_id=1 for MVP - no auth yet)
    doc = Document(
        user_id=1,
        filename=file.filename,
        filepath=filepath,
        file_type=suffix,
        file_size=len(content),
        content=text
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "content_preview": text[:500] + "..." if len(text) > 500 else text
    }


@router.get("/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document by ID"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "content": doc.content,
        "summary": doc.summary,
        "created_at": doc.created_at
    }


@router.post("/{document_id}/summarize")
async def summarize_document(document_id: int, db: Session = Depends(get_db)):
    """Generate LLM summary for a document"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    summary = await llm_service.summarize(doc.content)

    # Save summary
    doc.summary = summary
    db.commit()

    return {"id": doc.id, "summary": summary}


@router.post("/{document_id}/qa")
async def document_qa(
    document_id: int,
    question: str,
    db: Session = Depends(get_db)
):
    """Ask a question about a document"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    answer = await llm_service.qa(doc.content, question)
    return {"question": question, "answer": answer}


@router.get("/")
async def list_documents(db: Session = Depends(get_db)):
    """List all documents"""
    docs = db.query(Document).all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "created_at": doc.created_at,
            "has_summary": doc.summary is not None
        }
        for doc in docs
    ]


@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    await document_service.delete_file(doc.filepath)

    # Delete from DB
    db.delete(doc)
    db.commit()

    return {"message": "Document deleted"}
