from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.models.portfolio import Portfolio, Holding
from app.services.market_data import market_data_service

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


class HoldingCreate(BaseModel):
    symbol: str
    quantity: float
    avg_cost: Optional[float] = None


class PortfolioCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PortfolioAddHoldings(BaseModel):
    holdings: List[HoldingCreate]


@router.post("/")
async def create_portfolio(data: PortfolioCreate, db: Session = Depends(get_db)):
    """Create a new portfolio"""
    portfolio = Portfolio(
        user_id=1,  # MVP - no auth yet
        name=data.name,
        description=data.description
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return {"id": portfolio.id, "name": portfolio.name}


@router.get("/")
async def list_portfolios(db: Session = Depends(get_db)):
    """List all portfolios"""
    portfolios = db.query(Portfolio).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "holdings_count": len(p.holdings),
            "created_at": p.created_at
        }
        for p in portfolios
    ]


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Get portfolio with holdings and current values"""
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Get current prices for all holdings
    holdings_data = []
    total_value = 0
    total_cost = 0

    for holding in portfolio.holdings:
        quote = await market_data_service.get_quote(holding.symbol)
        current_price = quote.get("price", 0) or 0
        market_value = holding.quantity * current_price
        cost_basis = holding.quantity * (holding.avg_cost or 0)
        gain_loss = market_value - cost_basis if holding.avg_cost else None

        holdings_data.append({
            "id": holding.id,
            "symbol": holding.symbol,
            "quantity": holding.quantity,
            "avg_cost": holding.avg_cost,
            "current_price": current_price,
            "market_value": market_value,
            "gain_loss": gain_loss,
            "gain_loss_pct": (gain_loss / cost_basis * 100) if cost_basis else None
        })

        total_value += market_value
        total_cost += cost_basis

    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "description": portfolio.description,
        "holdings": holdings_data,
        "total_value": total_value,
        "total_cost": total_cost,
        "total_gain_loss": total_value - total_cost,
        "total_gain_loss_pct": ((total_value - total_cost) / total_cost * 100) if total_cost else None
    }


@router.post("/{portfolio_id}/holdings")
async def add_holdings(
    portfolio_id: int,
    data: PortfolioAddHoldings,
    db: Session = Depends(get_db)
):
    """Add holdings to a portfolio"""
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    added = []
    for h in data.holdings:
        holding = Holding(
            portfolio_id=portfolio_id,
            symbol=h.symbol.upper(),
            quantity=h.quantity,
            avg_cost=h.avg_cost
        )
        db.add(holding)
        added.append(h.symbol)

    db.commit()
    return {"message": f"Added {len(added)} holdings", "symbols": added}


@router.delete("/{portfolio_id}/holdings/{holding_id}")
async def remove_holding(
    portfolio_id: int,
    holding_id: int,
    db: Session = Depends(get_db)
):
    """Remove a holding from portfolio"""
    holding = db.query(Holding).filter(
        Holding.id == holding_id,
        Holding.portfolio_id == portfolio_id
    ).first()

    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    db.delete(holding)
    db.commit()
    return {"message": "Holding removed"}


@router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Delete a portfolio"""
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    db.delete(portfolio)
    db.commit()
    return {"message": "Portfolio deleted"}
