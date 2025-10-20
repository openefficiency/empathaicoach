"use client";

import React, { useState } from "react";
import { Button, Card, CardContent } from "@pipecat-ai/voice-ui-kit";
import { Upload, FileText, Loader2, CheckCircle2, AlertCircle } from "lucide-react";

interface FeedbackTheme {
  category: string;
  theme: string;
  frequency: number;
  examples: string[];
}

interface FeedbackInputProps {
  onFeedbackSubmit: (feedbackData: any) => void;
  userId: string;
}

export const FeedbackInput: React.FC<FeedbackInputProps> = ({
  onFeedbackSubmit,
  userId,
}) => {
  const [feedbackText, setFeedbackText] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [parsedThemes, setParsedThemes] = useState<FeedbackTheme[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = [".txt", ".csv", ".json"];
      const fileExtension = file.name.substring(file.name.lastIndexOf("."));
      
      if (!validTypes.includes(fileExtension.toLowerCase())) {
        setError("Please upload a .txt, .csv, or .json file");
        return;
      }
      
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!feedbackText && !selectedFile) {
      setError("Please enter feedback text or upload a file");
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadSuccess(false);

    try {
      let requestBody: any = {
        user_id: userId,
      };

      if (selectedFile) {
        // Read file and convert to base64
        const fileContent = await readFileAsText(selectedFile);
        const base64Content = btoa(fileContent);
        
        const fileExtension = selectedFile.name.substring(
          selectedFile.name.lastIndexOf(".") + 1
        );
        
        requestBody.feedback_file = base64Content;
        requestBody.file_type = fileExtension;
      } else if (feedbackText) {
        requestBody.feedback_text = feedbackText;
      }

      // Call the feedback upload API
      const response = await fetch("/api/feedback/upload", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to upload feedback");
      }

      const data = await response.json();
      
      // Store parsed themes
      setParsedThemes(data.parsed_themes || []);
      setUploadSuccess(true);
      
      // Pass the full feedback data to parent
      onFeedbackSubmit({
        feedback_id: data.feedback_id,
        themes: data.parsed_themes,
        total_comments: data.total_comments,
      });
      
    } catch (err) {
      console.error("Upload error:", err);
      setError(err instanceof Error ? err.message : "Failed to upload feedback");
      setUploadSuccess(false);
    } finally {
      setIsUploading(false);
    }
  };

  const readFileAsText = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = (e) => reject(e);
      reader.readAsText(file);
    });
  };

  const handleClear = () => {
    setFeedbackText("");
    setSelectedFile(null);
    setParsedThemes([]);
    setError(null);
    setUploadSuccess(false);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Upload Your 360° Feedback
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Share your feedback data to begin your R2C2 coaching session
        </p>
      </div>

      <Card>
        <CardContent className="space-y-4 pt-6">
          {/* Text Input */}
          <div className="space-y-2">
            <label
              htmlFor="feedback-text"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Paste Feedback Text
            </label>
            <textarea
              id="feedback-text"
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="Paste your 360° feedback comments here..."
              className="w-full h-40 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white resize-none"
              disabled={isUploading || uploadSuccess}
            />
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300 dark:border-gray-600"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white dark:bg-gray-800 text-gray-500">
                OR
              </span>
            </div>
          </div>

          {/* File Upload */}
          <div className="space-y-2">
            <label
              htmlFor="feedback-file"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Upload Feedback File
            </label>
            <div className="flex items-center gap-2">
              <label
                htmlFor="feedback-file"
                className="flex-1 flex items-center justify-center px-4 py-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-md cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
              >
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  {selectedFile ? (
                    <>
                      <FileText className="w-5 h-5" />
                      <span className="text-sm">{selectedFile.name}</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-5 h-5" />
                      <span className="text-sm">
                        Choose CSV, JSON, or TXT file
                      </span>
                    </>
                  )}
                </div>
                <input
                  id="feedback-file"
                  type="file"
                  accept=".txt,.csv,.json"
                  onChange={handleFileSelect}
                  className="hidden"
                  disabled={isUploading || uploadSuccess}
                />
              </label>
              {selectedFile && (
                <Button
                  variant="outline"
                  onClick={() => setSelectedFile(null)}
                  disabled={isUploading || uploadSuccess}
                >
                  Clear
                </Button>
              )}
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Supported formats: CSV, JSON, or plain text
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" />
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Success Message */}
          {uploadSuccess && (
            <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md">
              <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0" />
              <p className="text-sm text-green-600 dark:text-green-400">
                Feedback uploaded and parsed successfully!
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2">
            <Button
              onClick={handleUpload}
              disabled={isUploading || uploadSuccess || (!feedbackText && !selectedFile)}
              className="flex-1"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : uploadSuccess ? (
                "Uploaded"
              ) : (
                "Upload & Parse Feedback"
              )}
            </Button>
            {(feedbackText || selectedFile || parsedThemes.length > 0) && (
              <Button variant="outline" onClick={handleClear} disabled={isUploading}>
                Clear All
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Parsed Themes Preview */}
      {parsedThemes.length > 0 && (
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Feedback Themes Preview
            </h3>
            <div className="space-y-4">
              {parsedThemes.map((theme, index) => (
                <div
                  key={index}
                  className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {theme.theme}
                      </h4>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          theme.category === "strength"
                            ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400"
                            : theme.category === "improvement"
                            ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400"
                            : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-400"
                        }`}
                      >
                        {theme.category}
                      </span>
                    </div>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {theme.frequency} mention{theme.frequency !== 1 ? "s" : ""}
                    </span>
                  </div>
                  {theme.examples.length > 0 && (
                    <div className="mt-2 space-y-1">
                      <p className="text-xs font-medium text-gray-600 dark:text-gray-400">
                        Examples:
                      </p>
                      {theme.examples.map((example, exIdx) => (
                        <p
                          key={exIdx}
                          className="text-sm text-gray-600 dark:text-gray-400 pl-3 border-l-2 border-gray-300 dark:border-gray-600"
                        >
                          "{example}"
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
