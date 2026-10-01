import { useEffect, useRef, useState } from "react";
import "./App.css";

function parseEvidenceAnswer(answer = "") {
  const headingPattern = /^### Section (.+)$/gm;
  const headings = [...answer.matchAll(headingPattern)];

  if (!headings.length) {
    return { introductionBlocks: [], introduction: answer, sections: [] };
  }

  const introduction = answer.slice(0, headings[0].index).trim();
  const introHeadingPattern = /^### (.+)$/gm;
  const introHeadings = [...introduction.matchAll(introHeadingPattern)];
  const introductionBlocks = [];

  if (!introHeadings.length) {
    if (introduction) introductionBlocks.push({ heading: "", content: introduction });
  } else {
    if (introduction.slice(0, introHeadings[0].index).trim()) {
      introductionBlocks.push({
        heading: "",
        content: introduction.slice(0, introHeadings[0].index).trim(),
      });
    }

    introHeadings.forEach((heading, index) => {
      const contentStart = heading.index + heading[0].length;
      const contentEnd = introHeadings[index + 1]?.index ?? introduction.length;
      introductionBlocks.push({
        heading: heading[1].trim(),
        content: introduction.slice(contentStart, contentEnd).trim(),
      });
    });
  }

  const sections = headings.map((heading, index) => {
    const contentStart = heading.index + heading[0].length;
    const contentEnd = headings[index + 1]?.index ?? answer.length;
    const content = answer.slice(contentStart, contentEnd).trim();
    const excerptMarker = "Evidence excerpt:";

    return {
      heading: heading[1].trim(),
      excerpt: content.startsWith(excerptMarker)
        ? content.slice(excerptMarker.length).trim()
        : content,
    };
  });

  return { introductionBlocks, introduction, sections };
}

function sortCitations(citations = []) {
  return [...citations].sort((left, right) => {
    const leftSection = String(left.section ?? "");
    const rightSection = String(right.section ?? "");
    const sectionPattern = /^(\d+)(?:\((\d+)\))?$/;
    const leftParts = leftSection.match(sectionPattern);
    const rightParts = rightSection.match(sectionPattern);

    if (leftParts && rightParts) {
      const sectionOrder = Number(leftParts[1]) - Number(rightParts[1]);
      if (sectionOrder) return sectionOrder;
      return Number(leftParts[2] || 0) - Number(rightParts[2] || 0);
    }

    return leftSection.localeCompare(rightSection, undefined, { numeric: true });
  });
}

function excerptPreview(excerpt, maxLength = 280) {
  if (excerpt.length <= maxLength) return excerpt;

  const preview = excerpt.slice(0, maxLength).trimEnd();
  const paragraphBoundary = preview.lastIndexOf("\n\n");
  const sentenceBoundary = preview.lastIndexOf(". ");
  const boundary = Math.max(paragraphBoundary, sentenceBoundary);
  const end = boundary >= maxLength / 2 ? boundary + (boundary === sentenceBoundary ? 1 : 0) : preview.length;

  return `${preview.slice(0, end).trimEnd()}…`;
}

// Faithful conversion of the supplied HTML: the answer and voice input are demos.
export default function App() {
  const [textSize, setTextSize] = useState("standard");
  const [contrast, setContrast] = useState(false);
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [apiResult, setApiResult] = useState(null);
  const [apiError, setApiError] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [issue, setIssue] = useState(
    "I ordered a brand-new laptop for ₹64,000 from an online electronics store. When it arrived, the internal motherboard was malfunctioning and it would not boot. I reported it within 24 hours, but the seller refused a replacement or refund, telling me to contact the authorized brand service center instead.",
  );
  const timerRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => () => clearTimeout(timerRef.current), []);

  function toggleMicrophone() {
    clearTimeout(timerRef.current);
    if (recording) {
      setRecording(false);
      return;
    }
    setRecording(true);
    timerRef.current = setTimeout(() => setRecording(false), 4000);
  }
  function clearIssue() {
    setIssue("");
    inputRef.current?.focus();
  }
  function selectSample(text) {
    setIssue(text);
    inputRef.current?.focus();
    inputRef.current?.scrollIntoView({ block: "center", behavior: "smooth" });
  }
  function showVoiceGuide() {
    window.alert(
      "Audio Guide: 'Describe your issue in plain words or click one of the common situation buttons. Our system maps your issue to the Consumer Protection Act, 2019.'",
    );
  }
  async function findRights() {
    const trimmedIssue = issue.trim();

    if (!trimmedIssue) {
      setApiError("Please describe your issue before checking your rights.");
      setApiResult(null);
      return;
    }

    setLoading(true);
    setApiError("");
    setApiResult(null);

    try {
      const requestBody = { question: trimmedIssue };
      if (sessionId) requestBody.session_id = sessionId;

      const response = await fetch("/api/ask/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data?.detail || data?.error || "Unable to fetch legal guidance.");
      }

      setApiResult(data);
  if (data.session_id) setSessionId(data.session_id);
    } catch (error) {
      setApiError(error.message || "Something went wrong while checking your rights.");
    } finally {
      setLoading(false);
    }
  }

  const answerPresentation = parseEvidenceAnswer(apiResult?.answer || "");
  const sortedCitations = sortCitations(apiResult?.citations || []);

  return (
    <div
      className={`consumer-app min-h-screen flex flex-col antialiased selection:bg-amber-200 ${textSize === "large" ? "text-lg-mode" : textSize === "xl" ? "text-xl-mode" : ""} ${contrast ? "high-contrast" : ""}`}
    >
      <aside
        aria-label="Accessibility Bar"
        className="bg-slate-900 text-slate-200 text-xs py-2 px-4 border-b border-slate-800"
      >
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-4">
            <span className="font-semibold text-slate-400">{"TEXT SIZE:"}</span>
            <div className="inline-flex rounded-md shadow-sm" role="group">
              <button
                id="btn-text-std"
                type="button"
                onClick={() => setTextSize("standard")}
                className={`size-control ${textSize === "standard" ? "selected" : ""}`}
                aria-pressed={textSize === "standard"}
              >
                {"Standard"}
              </button>
              <button
                id="btn-text-lg"
                type="button"
                onClick={() => setTextSize("large")}
                className={`size-control ${textSize === "large" ? "selected" : ""}`}
                aria-pressed={textSize === "large"}
              >
                {"Large"}
              </button>
              <button
                id="btn-text-xl"
                type="button"
                onClick={() => setTextSize("xl")}
                className={`size-control ${textSize === "xl" ? "selected" : ""}`}
                aria-pressed={textSize === "xl"}
              >
                {"XL"}
              </button>
            </div>
            <button
              id="btn-toggle-contrast"
              className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 transition"
              type="button"
              onClick={() => setContrast(!contrast)}
              aria-pressed={contrast}
            >
              <svg
                className="w-3.5 h-3.5 text-amber-400"
                fill="none"
                stroke="currentColor"
                viewbox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                ></path>
              </svg>
              <span>{"High Contrast"}</span>
            </button>
            <button
              id="btn-voice-guide"
              className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 transition"
              type="button"
              onClick={showVoiceGuide}
            >
              <svg
                className="w-3.5 h-3.5 text-sky-400"
                fill="none"
                stroke="currentColor"
                viewbox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
                ></path>
              </svg>
              <span>{"Audio Voice Guide"}</span>
            </button>
          </div>
          <a
            href="tel:1915"
            className="inline-flex items-center gap-2 bg-amber-700 hover:bg-amber-600 text-white font-bold px-3.5 py-1 rounded-md text-xs shadow transition"
          >
            <svg
              className="w-3.5 h-3.5"
              fill="currentColor"
              viewbox="0 0 20 20"
            >
              <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 4V3z"></path>
            </svg>
            {" National Helpline: 1915 (Toll-Free) "}
          </a>
        </div>
      </aside>
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center text-amber-500 shadow">
              <svg
                className="w-6 h-6"
                viewbox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M12 3v18M6 8l6-3 6 3M3 13c0 3 4 3 4 0L6 8H3zm14 0c0 3 4 3 4 0l-1-5h-3zM8 21h8"></path>
              </svg>
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-slate-950 block">
                {"Consumer Rights"}
              </span>
              <span className="text-xs text-slate-500 font-medium">
                {"Consumer Protection Act, 2019 • Citizen Guide"}
              </span>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-1">
            <a
              href="#describe"
              className="px-4 py-2 rounded-lg text-sm font-semibold bg-slate-900 text-white shadow-sm"
            >
              {"Describe Your Issue"}
            </a>
            <a
              href="#problems"
              className="px-4 py-2 rounded-lg text-sm font-medium text-slate-700 hover:text-slate-950 hover:bg-slate-100 transition"
            >
              {"Common Problems"}
            </a>
            <a
              href="#rights"
              className="px-4 py-2 rounded-lg text-sm font-medium text-slate-700 hover:text-slate-950 hover:bg-slate-100 transition"
            >
              {"Know Your Rights"}
            </a>
            <a
              href="#about"
              className="px-4 py-2 rounded-lg text-sm font-medium text-slate-700 hover:text-slate-950 hover:bg-slate-100 transition"
            >
              {"About This Guide"}
            </a>
          </nav>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              {" Official CPA 2019 "}
            </span>
          </div>
        </div>
      </header>
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 bg-white border border-slate-200 rounded-2xl p-4 sm:p-6 shadow-sm">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <span className="text-xs uppercase tracking-wider font-bold text-amber-700 block">
                {"Plain Language Section Finder"}
              </span>
              <h1 className="serif-title text-2xl sm:text-3xl font-bold text-slate-900 mt-1">
                {"Describe What Happened in Your Own Words"}
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                {
                  "We identify the exact legal rights, sections, and evidence under the Consumer Protection Act, 2019."
                }
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs font-semibold self-stretch sm:self-auto overflow-x-auto pb-1">
              <span className="flex items-center gap-1.5 bg-amber-100 text-amber-900 px-3 py-1.5 rounded-full border border-amber-300 whitespace-nowrap">
                <span className="w-5 h-5 rounded-full bg-amber-600 text-white flex items-center justify-center text-[10px]">
                  {"1"}
                </span>
                {" Tell Your Story "}
              </span>
              <span className="text-slate-300">{"→"}</span>
              <span className="flex items-center gap-1.5 bg-slate-100 text-slate-700 px-3 py-1.5 rounded-full border border-slate-200 whitespace-nowrap">
                <span className="w-5 h-5 rounded-full bg-slate-300 text-slate-700 flex items-center justify-center text-[10px]">
                  {"2"}
                </span>
                {" Get Plain Sections "}
              </span>
              <span className="text-slate-300">{"→"}</span>
              <span className="flex items-center gap-1.5 bg-slate-100 text-slate-700 px-3 py-1.5 rounded-full border border-slate-200 whitespace-nowrap">
                <span className="w-5 h-5 rounded-full bg-slate-300 text-slate-700 flex items-center justify-center text-[10px]">
                  {"3"}
                </span>
                {" Next Steps & 1915 "}
              </span>
            </div>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <section className="lg:col-span-8 space-y-6" id="describe">
            <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-7 shadow-sm">
              <label
                htmlFor="issue-text"
                className="block text-base font-bold text-slate-900 mb-1"
              >
                {" What went wrong with your product or service? "}
              </label>
              <p className="text-xs sm:text-sm text-slate-500 mb-3">
                {
                  " No legal terms needed — write just like you would explain to a family member or friend. "
                }
              </p>
              <div className="relative">
                <textarea
                  id="issue-text"
                  rows="5"
                  maxLength={10000}
                  className="w-full border-2 border-slate-200 rounded-xl p-4 text-slate-900 text-base leading-relaxed focus:border-amber-600 focus:outline-none transition shadow-inner placeholder:text-slate-400"
                  placeholder="e.g. I ordered a brand new 55-inch television on Amazon for ₹38,000. When it arrived yesterday, the screen was cracked inside the box. The seller refused a replacement claiming 'customer induced damage'..."
                  value={issue}
                  onChange={(event) => setIssue(event.target.value)}
                  ref={inputRef}
                ></textarea>
                <div className="flex flex-wrap items-center justify-between gap-3 mt-3 pt-3 border-t border-slate-100">
                  <div className="flex items-center gap-2">
                    <button
                      id="btn-mic"
                      type="button"
                      onClick={toggleMicrophone}
                      className={
                        "inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 transition" +
                        (recording ? " bg-red-100 border-red-400" : "")
                      }
                      aria-pressed={recording}
                    >
                      <svg
                        className="w-4 h-4 text-red-600"
                        fill="currentColor"
                        viewbox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z"
                          clipRule="evenodd"
                        ></path>
                      </svg>
                      <span id="mic-label">
                        {recording
                          ? "Listening... Speak now"
                          : "Tap to Speak (Hindi / English)"}
                      </span>
                    </button>
                    <span className="text-xs text-slate-400 hidden sm:inline">
                      {"• Free & Private"}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      id="btn-clear"
                      type="button"
                      className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 transition"
                      onClick={clearIssue}
                    >
                      {"Clear"}
                    </button>
                    <button
                      id="btn-find"
                      type="button"
                      className="inline-flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-bold bg-amber-600 hover:bg-amber-700 text-white shadow-md hover:shadow-lg transition disabled:opacity-60 disabled:cursor-not-allowed"
                      onClick={findRights}
                      disabled={loading}
                    >
                      <span>{loading ? "Checking..." : "Find My Rights & Sections"}</span>
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewbox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M14 5l7 7m0 0l-7 7m7-7H3"
                        ></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              {apiError ? (
                <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  {apiError}
                </div>
              ) : null}

              {apiResult ? (
                <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
                  <div className="flex items-center justify-between gap-3 flex-wrap mb-2">
                    <span className="inline-flex items-center gap-2 rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-bold text-emerald-800 border border-emerald-200">
                      {apiResult.supported ? "Supported by legal data" : "Check review needed"}
                    </span>
                    <span className="text-xs text-slate-600">
                      Session: {apiResult.session_id?.slice(0, 8) || "new"}
                    </span>
                  </div>

                  {answerPresentation.sections.length ? (
                    <div className="mt-4 space-y-3">
                      {answerPresentation.introductionBlocks.map((block, index) => {
                        const lines = block.content.split("\n").map((line) => line.trim()).filter(Boolean);
                        const bullets = lines.length > 0 && lines.every((line) => line.startsWith("- "));
                        const headingStyle = block.heading.includes("does not establish")
                          ? "border-amber-400"
                          : block.heading.includes("relate to")
                            ? "border-slate-300"
                            : "border-emerald-500";

                        return (
                          <section
                            key={`${block.heading || "intro"}-${index}`}
                            className={block.heading ? `border-l-4 ${headingStyle} pl-4 py-1` : ""}
                          >
                            {block.heading ? (
                              <h3 className="text-sm font-bold text-slate-900 mb-1">
                                {block.heading}
                              </h3>
                            ) : null}
                            {bullets ? (
                              <ul className="space-y-2 text-sm leading-relaxed text-slate-700">
                                {lines.map((line, lineIndex) => (
                                  <li key={lineIndex} className="list-disc ml-5">
                                    {line.slice(2)}
                                  </li>
                                ))}
                              </ul>
                            ) : (
                              <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-700">
                                {block.content}
                              </p>
                            )}
                          </section>
                        );
                      })}
                      {answerPresentation.sections.map((section, index) => (
                        (() => {
                          const preview = excerptPreview(section.excerpt);
                          const hasMore = preview.length < section.excerpt.length;

                          return (
                            <article
                              key={`${section.heading}-${index}`}
                              className="rounded-xl border border-emerald-200 bg-white p-4 shadow-sm"
                            >
                              <h3 className="text-base font-bold leading-snug text-slate-900">
                                {section.heading}
                              </h3>
                              <div className="mt-3 border-l-2 border-amber-400 pl-3">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                                  Evidence excerpt
                                </span>
                                <p className="mt-1 whitespace-pre-wrap text-sm leading-relaxed text-slate-700">
                                  {preview}
                                </p>
                                {hasMore ? (
                                  <details className="mt-2">
                                    <summary className="cursor-pointer text-xs font-semibold text-emerald-800 hover:text-emerald-900">
                                      View retrieved excerpt
                                    </summary>
                                    <p className="mt-2 whitespace-pre-wrap border-t border-slate-100 pt-2 text-xs leading-relaxed text-slate-600">
                                      {section.excerpt}
                                    </p>
                                  </details>
                                ) : null}
                              </div>
                            </article>
                          );
                        })()
                      ))}
                    </div>
                  ) : (
                    <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-slate-800">
                      {apiResult.answer}
                    </p>
                  )}

                  {apiResult.citations?.length ? (
                    <div className="mt-4 border-t border-emerald-200 pt-4">
                      <div className="flex items-start justify-between gap-3 mb-3">
                        <div>
                          <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-600">
                            Legal Sources
                          </p>
                          <p className="mt-1 text-xs text-slate-500">
                            Sections retrieved from the Consumer Protection Act, 2019
                          </p>
                        </div>
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-emerald-800 border border-emerald-200">
                          <span className="inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
                          Verified
                        </span>
                      </div>

                      <ul className="space-y-2.5">
                        {sortedCitations.map((citation, index) => (
                          <li
                            key={`${citation.section || index}-${index}`}
                            className="flex items-start gap-3 rounded-xl border border-emerald-100 bg-white/80 p-3 shadow-sm"
                          >
                            <span className="mt-0.5 flex h-7 w-7 items-center justify-center rounded-md bg-emerald-100 text-emerald-700">
                              <svg
                                className="h-3.5 w-3.5"
                                viewBox="0 0 24 24"
                                fill="currentColor"
                                aria-hidden="true"
                              >
                                <path d="M7 3.5A2.5 2.5 0 0 1 9.5 1h7A2.5 2.5 0 0 1 19 3.5V20a1 1 0 0 1-1.52.85L13 18.2l-4.48 2.65A1 1 0 0 1 7 20V3.5Zm2.5-.5a.5.5 0 0 0-.5.5v15.17l3.48-2.06a1 1 0 0 1 1.04 0L15.5 18.17V3.5a.5.5 0 0 0-.5-.5h-5Z" />
                              </svg>
                            </span>

                            <div className="min-w-0 flex-1">
                              <div className="text-sm font-semibold text-slate-900">
                                Section {citation.section || "Unknown"}
                              </div>
                              {citation.title ? (
                                <div className="mt-0.5 text-xs text-slate-600 break-words">
                                  {citation.title}
                                </div>
                              ) : null}
                            </div>
                          </li>
                        ))}
                      </ul>

                      {Array.isArray(apiResult.claim_citations) && apiResult.claim_citations.length ? (
                        <details className="mt-4 overflow-hidden rounded-xl border border-slate-200 bg-white/70">
                          <summary className="cursor-pointer list-none px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">
                            View claim-level verification
                          </summary>

                          <div className="border-t border-slate-200 p-3 space-y-3">
                            {apiResult.claim_citations.map((claim, index) => (
                              <div
                                key={`${claim.claim || index}-${index}`}
                                className="rounded-lg border border-slate-200 bg-slate-50 p-3"
                              >
                                <div className="flex items-start justify-between gap-3">
                                  <p className="text-sm text-slate-800 leading-relaxed">
                                    {claim.claim}
                                  </p>

                                  {claim.supported === true ? (
                                    <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 text-xs font-bold">
                                      ✓
                                    </span>
                                  ) : (
                                    <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-amber-100 text-amber-700 text-xs font-bold">
                                      !
                                    </span>
                                  )}
                                </div>

                                {Array.isArray(claim.citations) && claim.citations.length ? (
                                  <ul className="mt-2 space-y-1.5 text-xs text-slate-600">
                                    {claim.citations.map((claimCitation, claimIndex) => (
                                      <li
                                        key={`${claimCitation.section || claimIndex}-${claimIndex}`}
                                        className="flex items-center gap-2"
                                      >
                                        <span className="inline-block h-2 w-2 rounded-full bg-emerald-500"></span>
                                        Section {claimCitation.section || "Unknown"}
                                      </li>
                                    ))}
                                  </ul>
                                ) : null}
                              </div>
                            ))}
                          </div>
                        </details>
                      ) : null}

                      <p className="mt-3 text-[11px] text-slate-500 leading-relaxed">
                        Sources are retrieved from the project's legal corpus. This system provides legal information, not legal advice.
                      </p>
                    </div>
                  ) : (
                    <div className="mt-4 border-t border-slate-200 pt-4">
                      <p className="text-sm text-slate-600">
                        No verified legal citations were returned for this answer.
                      </p>
                      <p className="mt-3 text-[11px] text-slate-500 leading-relaxed">
                        Sources are retrieved from the project's legal corpus. This system provides legal information, not legal advice.
                      </p>
                    </div>
                  )}
                </div>
              ) : null}

              <div
                className="mt-4 pt-3 border-t border-slate-100"
                id="problems"
              >
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">
                  {"Or click an everyday situation:"}
                </span>
                <div className="flex flex-wrap gap-2 text-xs">
                  <button
                    className="sample-chip px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-amber-50 hover:border-amber-300 border border-slate-200 text-slate-700 font-medium transition"
                    data-text="Airlines cancelled my domestic flight with 2 hours notice and refused a full refund, offering only a voucher valid for 3 months."
                    type="button"
                    onClick={() =>
                      selectSample(
                        "Airlines cancelled my domestic flight with 2 hours notice and refused a full refund, offering only a voucher valid for 3 months.",
                      )
                    }
                  >
                    {"✈️ Flight cancellation refund refused"}
                  </button>
                  <button
                    className="sample-chip px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-amber-50 hover:border-amber-300 border border-slate-200 text-slate-700 font-medium transition"
                    data-text="Restaurant added an automatic 10% 'Service Charge' of ₹420 to the dining bill and refused to remove it when asked."
                    type="button"
                    onClick={() =>
                      selectSample(
                        "Restaurant added an automatic 10% 'Service Charge' of \u20b9420 to the dining bill and refused to remove it when asked.",
                      )
                    }
                  >
                    {"🍽️ Forced service charge at restaurant"}
                  </button>
                  <button
                    className="sample-chip px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-amber-50 hover:border-amber-300 border border-slate-200 text-slate-700 font-medium transition"
                    data-text="I withdrew from a coaching institute after 15 days, and they refused to refund the remaining 11 months of advance fees paid."
                    type="button"
                    onClick={() =>
                      selectSample(
                        "I withdrew from a coaching institute after 15 days, and they refused to refund the remaining 11 months of advance fees paid.",
                      )
                    }
                  >
                    {"📚 Coaching institute refund refusal"}
                  </button>
                  <button
                    className="sample-chip px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-amber-50 hover:border-amber-300 border border-slate-200 text-slate-700 font-medium transition"
                    data-text="Online grocery app delivered expired infant formula milk and customer support bot closed the ticket without refund."
                    type="button"
                    onClick={() =>
                      selectSample(
                        "Online grocery app delivered expired infant formula milk and customer support bot closed the ticket without refund.",
                      )
                    }
                  >
                    {"🍼 Expired baby food delivered"}
                  </button>
                </div>
              </div>
            </div>
            <div className="border-l-4 border-emerald-600 bg-emerald-50/70 p-5 sm:p-6">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-800">
                Evidence-backed legal information
              </span>
              <h2 className="serif-title mt-2 text-xl font-bold text-slate-900">
                Review the provisions retrieved for your question
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-700">
                The answer above presents excerpts from retrieved legal sections and links them to verified corpus citations. It provides legal information, not a determination of entitlement or legal advice.
              </p>
            </div>
            <div className="space-y-4" id="rights">
              <div className="border-b border-slate-200 pb-3">
                <h3 className="text-sm font-bold text-slate-900">
                  About the legal sources
                </h3>
                <p className="mt-1 text-sm leading-relaxed text-slate-600">
                  The sources shown with each answer come from the project's legal corpus. Review the cited sections for the statutory wording relevant to your question; this guide does not assess individual facts or predict an outcome.
                </p>
              </div>
            </div>
          </section>
          <aside className="lg:col-span-4 space-y-6">
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <span>{"📋"}</span>
                  {" Essential Proof to Keep "}
                </h3>
                <span className="text-[11px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded">
                  {"Interactive"}
                </span>
              </div>
              <p className="text-xs text-slate-500 mb-3">
                Keep records that help document the purchase, issue, and communications. Relevant records vary by situation.
              </p>
              <div className="space-y-2.5 text-xs">
                <label className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-50 hover:bg-slate-100 cursor-pointer">
                  <input
                    type="checkbox"
                    className="mt-0.5 rounded text-amber-600 focus:ring-amber-500 w-4 h-4"
                    defaultChecked
                  />
                  <div>
                    <span className="font-bold text-slate-800 block">
                      {"Tax Invoice / Bill"}
                    </span>
                    <span className="text-slate-500">
                      {"Shows GST number, price, and purchase date."}
                    </span>
                  </div>
                </label>
                <label className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-50 hover:bg-slate-100 cursor-pointer">
                  <input
                    type="checkbox"
                    className="mt-0.5 rounded text-amber-600 focus:ring-amber-500 w-4 h-4"
                    defaultChecked
                  />
                  <div>
                    <span className="font-bold text-slate-800 block">
                      {"Photos of Box & Item"}
                    </span>
                    <span className="text-slate-500">
                      {"Clear photos showing serial number & defect."}
                    </span>
                  </div>
                </label>
                <label className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-50 hover:bg-slate-100 cursor-pointer">
                  <input
                    type="checkbox"
                    className="mt-0.5 rounded text-amber-600 focus:ring-amber-500 w-4 h-4"
                    defaultChecked
                  />
                  <div>
                    <span className="font-bold text-slate-800 block">
                      {"Support Chat or Email"}
                    </span>
                    <span className="text-slate-500">
                      {"Screenshots of refusal or ticket closure."}
                    </span>
                  </div>
                </label>
                <label className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-50 hover:bg-slate-100 cursor-pointer">
                  <input
                    type="checkbox"
                    className="mt-0.5 rounded text-amber-600 focus:ring-amber-500 w-4 h-4"
                  />
                  <div>
                    <span className="font-bold text-slate-800 block">
                      {"Courier Delivery Slip"}
                    </span>
                    <span className="text-slate-500">
                      {"SMS or delivery confirmation date."}
                    </span>
                  </div>
                </label>
              </div>
            </div>
            <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-md border border-slate-800">
              <div className="flex items-center justify-between text-xs mb-3 text-slate-400">
                <span className="uppercase tracking-wider font-bold text-emerald-400">
                  {"Consumer Helpline"}
                </span>
                <span>{"National Consumer Helpline"}</span>
              </div>
              <h4 className="text-lg font-bold text-white mb-1">
                {"Looking for official consumer resources?"}
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed mb-4">
                Contact the National Consumer Helpline for information about consumer complaint channels.
              </p>
              <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700 mb-4 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                    {"Toll-Free Helpline"}
                  </span>
                  <span className="text-2xl font-extrabold text-white tracking-wide">
                    {"1915"}
                  </span>
                </div>
                <a
                  href="tel:1915"
                  className="inline-flex items-center gap-2 bg-amber-600 hover:bg-amber-500 text-white font-bold text-sm px-4 py-2 rounded-lg shadow transition"
                >
                  <svg
                    className="w-4 h-4"
                    fill="currentColor"
                    viewbox="0 0 20 20"
                  >
                    <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 4V3z"></path>
                  </svg>
                  <span>{"Dial 1915"}</span>
                </a>
              </div>
              <p className="text-[11px] text-slate-400 text-center">
                {"Open 9:30 AM to 5:30 PM (except gazetted national holidays)"}
              </p>
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
              <span className="text-xs uppercase tracking-wider font-bold text-amber-700 block mb-1">
                {"Next Steps Guide"}
              </span>
              <h4 className="text-sm font-bold text-slate-900 mb-3">
                {"Practical steps to consider"}
              </h4>
              <ol className="space-y-3 text-xs text-slate-700">
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-slate-900 text-white flex-shrink-0 flex items-center justify-center font-bold text-[10px]">
                    {"1"}
                  </span>
                  <div>
                    <strong>{"Keep relevant records:"}</strong>
                    Save receipts, order details, messages, and other records related to the issue.
                  </div>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-slate-900 text-white flex-shrink-0 flex items-center justify-center font-bold text-[10px]">
                    {"2"}
                  </span>
                  <div>
                    <strong>{"Document communications:"}</strong>
                    Keep copies of written communications with the seller or service provider.
                  </div>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-slate-900 text-white flex-shrink-0 flex items-center justify-center font-bold text-[10px]">
                    {"3"}
                  </span>
                  <div>
                    <strong>{"Review official guidance:"}</strong>
                    Check current complaint procedures with an official consumer resource or qualified adviser.
                  </div>
                </li>
              </ol>
            </div>
          </aside>
        </div>
      </main>
      <footer
        className="bg-slate-900 text-slate-300 border-t border-slate-800 mt-12 py-8 px-4 text-xs"
        id="about"
      >
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <p className="font-semibold text-white">
              {"Consumer Rights Citizen Guide • Act No. 35 of 2019"}
            </p>
            <p className="text-slate-400 mt-0.5">
              {
                "A public legal literacy project. Not an official court registry or legal counsel portal."
              }
            </p>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <span>
              {"Toll-Free Helpline: "}
              <strong>{"1915"}</strong>
            </span>
            <span>{"•"}</span>
            <span>
              {"SMS Support: "}
              <strong>{"8800001915"}</strong>
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
