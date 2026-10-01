import { useEffect, useState } from "react";
import Icon from "./Icon";

export default function ReadAloud({ text }) {
  const [reading, setReading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    return () => {
      window.speechSynthesis?.cancel();
    };
  }, []);

  function readText() {
    if (!window.speechSynthesis) {
      setMessage("Reading aloud is unavailable in this browser.");
      return;
    }

    window.speechSynthesis.cancel();

    if (reading) {
      setReading(false);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.lang = "en-IN";
    utterance.rate = 0.9;

    utterance.onend = () => {
      setReading(false);
    };

    utterance.onerror = () => {
      setReading(false);
      setMessage("Could not read aloud. Please try again.");
    };

    setMessage("");
    setReading(true);

    window.speechSynthesis.speak(utterance);
  }

  return (
    <div>
      <button
        type="button"
        className="text-button"
        onClick={readText}
      >
        <Icon name="sound" size={18} />

        {reading ? "Stop reading" : "Read aloud"}
      </button>

      {message && (
        <p
          role="status"
          className="small"
        >
          {message}
        </p>
      )}
    </div>
  );
}