import { useEffect, useRef, useState } from "react";
import { problems, suggestTopics } from "../data";
import Icon from "../components/Icon";
import ProblemDetail from "../components/ProblemDetail";

export default function Understand({
  draft,
  setDraft,
  selected,
  setSelected,
}) {
  const [language, setLanguage] = useState("en-IN");
  const [listening, setListening] = useState(false);
  const [status, setStatus] = useState("");
  const [suggestions, setSuggestions] = useState(null);

  const recognition = useRef(null);
  const resultRef = useRef(null);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;

    return () => {
      alive.current = false;
      recognition.current?.abort();
    };
  }, []);

  const supported =
    typeof window !== "undefined" &&
    Boolean(
      window.SpeechRecognition || window.webkitSpeechRecognition,
    );

  function record() {
    if (listening) {
      recognition.current?.stop();
      return;
    }

    const Speech =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!Speech) {
      setStatus(
        "Voice input is unavailable here. Type below or select a situation.",
      );
      return;
    }

    const session = new Speech();

    recognition.current = session;
    session.lang = language;
    session.continuous = false;
    session.interimResults = false;

    session.onstart = () => {
      if (alive.current) {
        setListening(true);
        setStatus("Listening. Speak now, then pause.");
      }
    };

    session.onresult = (event) => {
      if (!alive.current) return;

      const transcript =
        event.results[0][0].transcript;

      setDraft((oldText) =>
        oldText ? `${oldText} ${transcript}` : transcript,
      );

      setSuggestions(null);
      setSelected(null);
      setStatus(
        "Voice added. Check the words below before finding a topic.",
      );
    };

    session.onerror = (event) => {
      if (!alive.current) return;

      setListening(false);

      const messages = {
        "not-allowed":
          "Microphone permission was denied. Allow it in your browser or type below.",

        "no-speech":
          "No speech was heard. Try again or choose a situation below.",

        network:
          "The speech service could not connect. Check your connection or type below.",

        "language-not-supported":
          "This browser's speech service does not support the selected language. You can still type or choose a situation.",

        "audio-capture":
          "No microphone was found. Type or choose a situation below.",
      };

      setStatus(
        messages[event.error] ||
          "Voice input stopped. Try again or type below.",
      );
    };

    session.onend = () => {
      if (alive.current) {
        setListening(false);

        setStatus((oldStatus) =>
          oldStatus === "Listening. Speak now, then pause."
            ? "Recording ended. You can try again."
            : oldStatus,
        );
      }
    };

    try {
      setStatus("Starting microphone…");
      session.start();
    } catch {
      setStatus(
        "Could not start voice input. Please try again.",
      );
    }
  }

  function choose(problem) {
    setSelected(problem.id);

    requestAnimationFrame(() => {
      resultRef.current?.focus();

      resultRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }

  function findTopic(event) {
    event.preventDefault();

    if (!draft.trim()) {
      setStatus(
        "Describe a problem or select one of the situations below.",
      );
      return;
    }

    setSelected(null);
    setSuggestions(suggestTopics(draft));
    setStatus("");
  }

  const chosen = problems.find(
    (problem) => problem.id === selected,
  );

  return (
    <>
      <section className="hero">
        <div>
          <p className="eyebrow">
            Everyday purchases. Everyday rights.
          </p>

          <h1>
            A little clarity.
            <br />
            <em>A more confident you.</em>
          </h1>

          <p className="hero-copy">
            Something wrong with a purchase? Start with what happened.
            We’ll help you explore the consumer rights that may relate to
            it.
          </p>

          <a
            className="button primary"
            href="#problem-input"
          >
            Understand my problem
            <Icon name="arrow" />
          </a>

          <span className="hero-foot">
            No legal words needed. No account needed.
          </span>
        </div>

        <div
          className="hero-illustration"
          aria-hidden="true"
        >
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="paper paper-back" />

          <div className="paper">
            <span className="paper-label">
              YOUR EVERYDAY GUIDE
            </span>

            <Icon name="balance" size={66} />

            <h2>
              Know more.
              <br />
              Worry less.
            </h2>

            <div className="paper-line" />
            <div className="paper-line short" />

            <span className="seal">
              <Icon name="check" size={25} />
            </span>
          </div>

          <span className="floating-tag">
            <Icon name="shield" size={19} />
            Your rights matter
          </span>
        </div>
      </section>

      <div className="journey-strip">
        <span>
          <b>01</b>
          Tell us what happened
        </span>

        <span>
          <b>02</b>
          Choose the closest topic
        </span>

        <span>
          <b>03</b>
          Understand the section
        </span>
      </div>

      <section
        className="workspace"
        id="problem-input"
      >
        <div className="input-card">
          <p className="eyebrow">Start here</p>

          <h2>Tell it in your own words.</h2>

          <p>
            Speak in English or Malayalam. All guidance stays in English.
          </p>

          <div className="voice-row">
            <label>
              Voice language

              <select
                value={language}
                disabled={listening}
                onChange={(event) =>
                  setLanguage(event.target.value)
                }
              >
                <option value="en-IN">English</option>
                <option value="ml-IN">Malayalam</option>
              </select>
            </label>

            <button
              type="button"
              className={`button voice-button ${
                listening ? "listening" : ""
              }`}
              onClick={record}
              disabled={!supported}
            >
              <Icon name="voice" />

              {listening
                ? "Stop listening"
                : "Speak your problem"}
            </button>
          </div>

          <p className="small muted">
            {supported
              ? "Your browser may send audio to its speech service. Language availability varies by browser. Review the transcript before continuing."
              : "Voice is unavailable in this browser. You can type or choose a situation instead."}
          </p>

          <form onSubmit={findTopic}>
            <label htmlFor="problem">
              Or type what happened
            </label>

            <textarea
              id="problem"
              rows="4"
              maxLength={2000}
              value={draft}
              onChange={(event) => {
                setDraft(event.target.value);
                setSuggestions(null);
                setSelected(null);
              }}
              placeholder="For example: I bought a mixer and it stopped working after two days."
            />

            <div className="input-footer">
              <span className="small muted">
                No names or personal details needed.
              </span>

              <button
                type="submit"
                className="button primary"
                disabled={listening}
              >
                Find a topic
                <Icon name="arrow" size={18} />
              </button>
            </div>
          </form>

          <p
            role="status"
            className="status"
          >
            {status}
          </p>

          {suggestions !== null && (
            <div
              className="suggestions"
              aria-live="polite"
            >
              <h3>
                {suggestions.length
                  ? "Which topic fits best?"
                  : "Let’s choose a topic together."}
              </h3>

              <p className="small">
                {suggestions.length
                  ? "These are keyword suggestions. Confirm the closest situation below."
                  : "There is no clear keyword match. Choose a situation below, or describe the purchase and what went wrong."}
              </p>

              {suggestions.map((problem) => (
                <button
                  type="button"
                  className="suggestion"
                  key={problem.id}
                  onClick={() => choose(problem)}
                >
                  {problem.title}
                  <Icon name="arrow" size={18} />
                </button>
              ))}
            </div>
          )}
        </div>

        <aside className="quick-panel">
          <p className="eyebrow">
            Prefer not to type?
          </p>

          <h2>Choose a situation.</h2>

          <p>One tap is enough to get started.</p>

          {problems.slice(0, 4).map((problem) => (
            <button
              type="button"
              className="quick-choice"
              key={problem.id}
              onClick={() => choose(problem)}
            >
              <span className="icon-box">
                <Icon name={problem.icon} />
              </span>

              <span>{problem.title}</span>

              <Icon name="arrow" size={17} />
            </button>
          ))}

          <a
            className="text-button"
            href="#/problems"
          >
            See all common problems
            <Icon name="arrow" size={18} />
          </a>
        </aside>
      </section>

      {chosen && (
        <div
          ref={resultRef}
          tabIndex={-1}
          className="result-anchor"
        >
          <ProblemDetail problem={chosen} />
        </div>
      )}

      <section className="learning-banner">
        <div className="icon-box">
          <Icon name="book" size={30} />
        </div>

        <div>
          <p className="eyebrow">
            A good place to begin
          </p>

          <h2>
            You have six basic consumer rights.
          </h2>

          <p>
            Learn them through small, everyday examples.
          </p>
        </div>

        <a
          className="button secondary"
          href="#/rights"
        >
          Explore your rights
          <Icon name="arrow" size={18} />
        </a>
      </section>
    </>
  );
}