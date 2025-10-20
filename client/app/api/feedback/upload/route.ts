import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Get backend URL from environment or use default
    const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:7860";
    
    // Forward request to backend
    const response = await fetch(`${backendUrl}/api/feedback/upload`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      return NextResponse.json(
        { detail: data.detail || "Failed to upload feedback" },
        { status: response.status }
      );
    }
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Feedback upload proxy error:", error);
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    );
  }
}
