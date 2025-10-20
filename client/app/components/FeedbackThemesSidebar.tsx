"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronRight, MessageSquare } from "lucide-react";

interface FeedbackTheme {
  category: string;
  theme: string;
  frequency: number;
  examples: string[];
}

interface FeedbackThemesSidebarProps {
  themes: FeedbackTheme[];
  discussedThemes?: string[];
  onThemeClick?: (theme: string) => void;
}

const getCategoryColor = (category: string): string => {
  const categoryColors: Record<string, string> = {
    strength: "text-green-600 dark:text-green-400",
    improvement: "text-orange-600 dark:text-orange-400",
    neutral: "text-gray-600 dark:text-gray-400",
  };
  return categoryColors[category.toLowerCase()] || "text-gray-600 dark:text-gray-400";
};

const getCategoryBgColor = (category: string): string => {
  const categoryBgColors: Record<string, string> = {
    strength: "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800",
    improvement: "bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800",
    neutral: "bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700",
  };
  return categoryBgColors[category.toLowerCase()] || "bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700";
};

const getCategoryIcon = (category: string): string => {
  const categoryIcons: Record<string, string> = {
    strength: "✓",
    improvement: "→",
    neutral: "•",
  };
  return categoryIcons[category.toLowerCase()] || "•";
};

export const FeedbackThemesSidebar: React.FC<FeedbackThemesSidebarProps> = ({
  themes,
  discussedThemes = [],
  onThemeClick,
}) => {
  const [expandedThemes, setExpandedThemes] = useState<Set<string>>(new Set());

  const toggleTheme = (theme: string) => {
    setExpandedThemes((prev) => {
      const next = new Set(prev);
      if (next.has(theme)) {
        next.delete(theme);
      } else {
        next.add(theme);
      }
      return next;
    });
  };

  const isThemeDiscussed = (theme: string): boolean => {
    return discussedThemes.some((discussed) =>
      theme.toLowerCase().includes(discussed.toLowerCase()) ||
      discussed.toLowerCase().includes(theme.toLowerCase())
    );
  };

  // Group themes by category
  const themesByCategory = themes.reduce((acc, theme) => {
    const category = theme.category || "neutral";
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(theme);
    return acc;
  }, {} as Record<string, FeedbackTheme[]>);

  // Sort categories: strength, improvement, neutral
  const sortedCategories = Object.keys(themesByCategory).sort((a, b) => {
    const order = ["strength", "improvement", "neutral"];
    return order.indexOf(a.toLowerCase()) - order.indexOf(b.toLowerCase());
  });

  if (themes.length === 0) {
    return (
      <div className="h-full flex items-center justify-center p-4 text-gray-400 dark:text-gray-600">
        <div className="text-center">
          <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No feedback themes available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <MessageSquare className="w-5 h-5" />
          Feedback Themes
        </h3>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Key themes from your 360° feedback
        </p>
      </div>

      {/* Themes list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {sortedCategories.map((category) => (
          <div key={category} className="space-y-2">
            {/* Category header */}
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide">
              <span className={getCategoryColor(category)}>
                {getCategoryIcon(category)} {category}
              </span>
              <span className="text-gray-400 dark:text-gray-600">
                ({themesByCategory[category].length})
              </span>
            </div>

            {/* Themes in this category */}
            {themesByCategory[category].map((theme, index) => {
              const isExpanded = expandedThemes.has(theme.theme);
              const isDiscussed = isThemeDiscussed(theme.theme);

              return (
                <div
                  key={`${category}-${index}`}
                  className={`rounded-lg border p-3 transition-all ${getCategoryBgColor(
                    category
                  )} ${
                    isDiscussed
                      ? "opacity-60 border-dashed"
                      : "opacity-100"
                  } ${
                    onThemeClick
                      ? "cursor-pointer hover:shadow-md"
                      : ""
                  }`}
                  onClick={() => onThemeClick?.(theme.theme)}
                >
                  {/* Theme header */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {theme.theme}
                        </p>
                        {isDiscussed && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
                            Discussed
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Mentioned {theme.frequency} time{theme.frequency !== 1 ? "s" : ""}
                      </p>
                    </div>
                    {theme.examples && theme.examples.length > 0 && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleTheme(theme.theme);
                        }}
                        className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      >
                        {isExpanded ? (
                          <ChevronDown className="w-4 h-4" />
                        ) : (
                          <ChevronRight className="w-4 h-4" />
                        )}
                      </button>
                    )}
                  </div>

                  {/* Examples (expandable) */}
                  {isExpanded && theme.examples && theme.examples.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                      <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
                        Examples:
                      </p>
                      <ul className="space-y-1">
                        {theme.examples.slice(0, 3).map((example, i) => (
                          <li
                            key={i}
                            className="text-xs text-gray-600 dark:text-gray-400 pl-3 border-l-2 border-gray-300 dark:border-gray-600"
                          >
                            "{example}"
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {/* Footer with legend */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Click on a theme to reference it during your conversation
        </p>
      </div>
    </div>
  );
};
