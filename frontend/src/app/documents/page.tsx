"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";

interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  created_at: string;
  has_summary: boolean;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const fetchDocuments = async () => {
    try {
      const data = await api.get("/documents/");
      setDocuments(data);
    } catch (error) {
      console.error("Failed to fetch documents:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await api.uploadFile("/documents/upload", file);
      await fetchDocuments();
    } catch (error) {
      alert(`Upload failed: ${error}`);
    } finally {
      setUploading(false);
    }
  };

  const handleSummarize = async (id: number) => {
    try {
      await api.post(`/documents/${id}/summarize`, {});
      await fetchDocuments();
    } catch (error) {
      alert(`Summarization failed: ${error}`);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Documents</h1>
          <p className="text-gray-400 mt-1">Upload and analyze financial documents with AI</p>
        </div>
        <label className="cursor-pointer">
          <input
            type="file"
            className="hidden"
            accept=".pdf,.txt,.docx"
            onChange={handleUpload}
            disabled={uploading}
          />
          <span className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            uploading
              ? "bg-gray-700 text-gray-400 cursor-not-allowed"
              : "bg-blue-600 text-white hover:bg-blue-700"
          }`}>
            {uploading ? "Uploading..." : "Upload Document"}
          </span>
        </label>
      </div>

      {/* Documents Table */}
      <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <p className="text-gray-400">Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center">
            <div className="w-16 h-16 rounded-full bg-[#2a2a3a] flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">📄</span>
            </div>
            <p className="text-gray-300 font-medium">No documents uploaded yet</p>
            <p className="text-gray-500 text-sm mt-1">Upload a PDF, TXT, or DOCX file to get started</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#2a2a3a]">
                <th className="text-left py-4 px-6 text-gray-400 font-medium text-sm">Filename</th>
                <th className="text-left py-4 px-6 text-gray-400 font-medium text-sm">Type</th>
                <th className="text-left py-4 px-6 text-gray-400 font-medium text-sm">Size</th>
                <th className="text-left py-4 px-6 text-gray-400 font-medium text-sm">Status</th>
                <th className="text-left py-4 px-6 text-gray-400 font-medium text-sm">Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id} className="border-b border-[#2a2a3a] hover:bg-[#22222e]">
                  <td className="py-4 px-6 text-white">{doc.filename}</td>
                  <td className="py-4 px-6 text-gray-400">{doc.file_type}</td>
                  <td className="py-4 px-6 text-gray-400">{formatFileSize(doc.file_size)}</td>
                  <td className="py-4 px-6">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      doc.has_summary
                        ? "bg-green-500/20 text-green-400"
                        : "bg-gray-500/20 text-gray-400"
                    }`}>
                      {doc.has_summary ? "Summarized" : "Pending"}
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    <div className="flex gap-2">
                      {!doc.has_summary && (
                        <button
                          onClick={() => handleSummarize(doc.id)}
                          className="px-3 py-1 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          Summarize
                        </button>
                      )}
                      <button className="px-3 py-1 bg-[#2a2a3a] text-gray-300 text-xs rounded-lg hover:bg-[#3a3a4a] transition-colors">
                        View
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
