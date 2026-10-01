import { useEffect, useRef, useState } from "react";
import "./App.css";

// Faithful conversion of the supplied HTML: the answer and voice input are demos.
export default function App() {
  const [textSize, setTextSize] = useState("standard");
  const [contrast, setContrast] = useState(false);
  const [recording, setRecording] = useState(false);
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
  function findRights() {
    window.alert(
      "Rights analyzed! Sections 2(10), 2(11), and 84 apply to your issue.",
    );
  }
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
                      className="inline-flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-bold bg-amber-600 hover:bg-amber-700 text-white shadow-md hover:shadow-lg transition"
                      onClick={findRights}
                    >
                      <span>{"Find My Rights & Sections"}</span>
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
            <div className="bg-gradient-to-br from-blue-50/70 to-indigo-50/40 border border-blue-200 rounded-2xl p-6 sm:p-7 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-900 border border-blue-200">
                  {" ⚖️ What the law says about your situation "}
                </span>
                <span className="text-xs font-semibold text-blue-800">
                  {"High Legal Certainty (99%)"}
                </span>
              </div>
              <h2 className="serif-title text-xl font-bold text-slate-900 mb-2">
                {
                  " You are entitled to a full replacement or refund. The seller cannot dodge liability. "
                }
              </h2>
              <p className="text-sm text-slate-700 leading-relaxed mb-4">
                {
                  " Under the Consumer Protection Act, 2019, passing the buck to the brand's service center is explicitly considered a "
                }
                <strong>{"“Deficiency in Service”"}</strong>
                {
                  ". E-commerce marketplaces and sellers are jointly accountable for delivering goods free from defects. "
                }
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-blue-200/60 text-xs">
                <div className="bg-white/80 p-3 rounded-xl border border-blue-100">
                  <span className="font-bold text-blue-900 block mb-0.5">
                    {"1. No Waiver Clauses"}
                  </span>
                  <span className="text-slate-600">
                    {
                      '"Goods once sold cannot be returned" is legally void under Section 2(47).'
                    }
                  </span>
                </div>
                <div className="bg-white/80 p-3 rounded-xl border border-blue-100">
                  <span className="font-bold text-blue-900 block mb-0.5">
                    {"2. Joint Product Liability"}
                  </span>
                  <span className="text-slate-600">
                    {
                      "Both seller and maker must rectify defects under Section 84 & 86."
                    }
                  </span>
                </div>
                <div className="bg-white/80 p-3 rounded-xl border border-blue-100">
                  <span className="font-bold text-blue-900 block mb-0.5">
                    {"3. 48-Hour Acknowledgment"}
                  </span>
                  <span className="text-slate-600">
                    {
                      "E-commerce Rules mandate resolving citizen grievances within 1 month."
                    }
                  </span>
                </div>
              </div>
            </div>
            <div className="space-y-4" id="rights">
              <h3 className="text-sm uppercase tracking-wider font-bold text-slate-500">
                {" Applicable Sections in Act No. 35 of 2019: "}
              </h3>
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:border-slate-300 transition">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2.5 py-0.5 text-xs font-extrabold rounded bg-slate-900 text-white">
                        {"Section 2(10)"}
                      </span>
                      <span className="text-sm font-bold text-slate-900">
                        {"“Defect in Goods”"}
                      </span>
                      <span className="text-xs bg-amber-100 text-amber-800 font-semibold px-2 py-0.5 rounded">
                        {"Core Ground"}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 mt-1">
                      <strong>{"In Plain Words:"}</strong>
                      {
                        " Any imperfection, shortcoming, or failure in quality, performance, or purity required by law or contract. A dead motherboard on arrival is a textbook statutory defect. "
                      }
                    </p>
                  </div>
                </div>
                <details className="mt-3 pt-3 border-t border-slate-100 text-xs">
                  <summary className="cursor-pointer font-bold text-amber-700 hover:text-amber-800 flex items-center gap-1 select-none">
                    <span>{"View Official Bare Act Gazette Text"}</span>
                  </summary>
                  <div className="mt-2 p-3 bg-slate-50 rounded-lg text-slate-700 font-serif italic border border-slate-200 leading-relaxed">
                    {
                      " “‘defect’ means any fault, imperfection or shortcoming in the quality, quantity, potency, purity or standard which is required to be maintained by or under any law for the time being in force or under any contract, express or implied...” "
                    }
                  </div>
                </details>
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:border-slate-300 transition">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2.5 py-0.5 text-xs font-extrabold rounded bg-slate-900 text-white">
                        {"Section 2(11)"}
                      </span>
                      <span className="text-sm font-bold text-slate-900">
                        {"“Deficiency in Service”"}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 mt-1">
                      <strong>{"In Plain Words:"}</strong>
                      {
                        " Refusing legitimate return requests or directing customers away from lawful resolution constitutes administrative and contractual deficiency by the seller. "
                      }
                    </p>
                  </div>
                </div>
                <details className="mt-3 pt-3 border-t border-slate-100 text-xs">
                  <summary className="cursor-pointer font-bold text-amber-700 hover:text-amber-800 flex items-center gap-1 select-none">
                    <span>{"View Official Bare Act Gazette Text"}</span>
                  </summary>
                  <div className="mt-2 p-3 bg-slate-50 rounded-lg text-slate-700 font-serif italic border border-slate-200 leading-relaxed">
                    {
                      " “‘deficiency’ means any fault, imperfection, shortcoming or inadequacy in the quality, nature and manner of performance which is required to be maintained by or under any law or in pursuance of a contract...” "
                    }
                  </div>
                </details>
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:border-slate-300 transition">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2.5 py-0.5 text-xs font-extrabold rounded bg-slate-900 text-white">
                        {"Sections 84 & 86"}
                      </span>
                      <span className="text-sm font-bold text-slate-900">
                        {"“Strict Product Liability Action”"}
                      </span>
                      <span className="text-xs bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded">
                        {"Remedy"}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 mt-1">
                      <strong>{"In Plain Words:"}</strong>
                      {
                        " A product seller or e-commerce entity is legally bound to compensate you or replace goods if they fail to conform to an express warranty or prevent lawful inspection. "
                      }
                    </p>
                  </div>
                </div>
                <details className="mt-3 pt-3 border-t border-slate-100 text-xs">
                  <summary className="cursor-pointer font-bold text-amber-700 hover:text-amber-800 flex items-center gap-1 select-none">
                    <span>{"View Official Bare Act Gazette Text"}</span>
                  </summary>
                  <div className="mt-2 p-3 bg-slate-50 rounded-lg text-slate-700 font-serif italic border border-slate-200 leading-relaxed">
                    {
                      " “A product manufacturer shall be liable in a product liability action if the product contains a manufacturing defect, or deviates from manufacturing specifications, or does not conform to an express warranty...” "
                    }
                  </div>
                </details>
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
                {
                  "Check what you have ready. Don't worry if missing one — your Tax Invoice is the key!"
                }
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
                  {"● Sovereign Redressal"}
                </span>
                <span>{"Dept. of Consumer Affairs"}</span>
              </div>
              <h4 className="text-lg font-bold text-white mb-1">
                {"Need a human advisor right now?"}
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed mb-4">
                {
                  " Guidance is 100% free and run by the Government of India. Available in English, Hindi, and 12 regional languages. "
                }
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
                {"3 Simple Steps You Can Take Today"}
              </h4>
              <ol className="space-y-3 text-xs text-slate-700">
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-slate-900 text-white flex-shrink-0 flex items-center justify-center font-bold text-[10px]">
                    {"1"}
                  </span>
                  <div>
                    <strong>{"Save invoice & chats:"}</strong>
                    {
                      " Keep clear screenshots of the refusal message on your phone. "
                    }
                  </div>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-slate-900 text-white flex-shrink-0 flex items-center justify-center font-bold text-[10px]">
                    {"2"}
                  </span>
                  <div>
                    <strong>{"Call 1915 or send written notice:"}</strong>
                    {
                      " Quote Section 2(10) Defect and demand a replacement within 48 hours. "
                    }
                  </div>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-slate-900 text-white flex-shrink-0 flex items-center justify-center font-bold text-[10px]">
                    {"3"}
                  </span>
                  <div>
                    <strong>{"Online filing (e-Daakhil):"}</strong>
                    {
                      " If ignored, file on edaakhil.nic.in without requiring an advocate. "
                    }
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
