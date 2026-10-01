import { ACT_URL } from "../data";
import ReadAloud from "./ReadAloud";

export default function ProblemDetail({ problem }) {
  return (
    <article className="result-card">
      <div className="result-top">
        <span className="eyebrow">
          A section to understand
        </span>

        <span className="tag">
          Consumer Protection Act, 2019
        </span>
      </div>

      <h2>{problem.term}</h2>

      <a
        className="section-link"
        href={ACT_URL}
        target="_blank"
        rel="noreferrer"
      >
        Section {problem.section} · Read the Act ↗
      </a>

      <p className="lead">
        {problem.explanation}
      </p>

      <div className="note">
        <strong>
          What matters in your situation
        </strong>

        <p>
          {problem.check}
        </p>
      </div>

      <h3>
        Useful details to keep
      </h3>

      <ul className="check-list">
        {problem.records.map((record) => (
          <li key={record}>
            {record}
          </li>
        ))}
      </ul>

      <div className="result-bottom">
        <ReadAloud
          text={`${problem.term}. Section ${problem.section}. ${problem.explanation} ${problem.check}`}
        />

        <button
          type="button"
          className="text-button"
          onClick={() => window.print()}
        >
          Print this guide ↗
        </button>
      </div>

      <p className="small muted">
        This is an educational starting point, not a decision that a law has
        been broken. Other facts or laws may affect the situation.
      </p>
    </article>
  );
}