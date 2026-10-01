import { useRef, useState } from "react";
import { problems } from "../data";
import Icon from "../components/Icon";
import ProblemDetail from "../components/ProblemDetail";

export default function CommonProblems() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("All");
  const [selected, setSelected] = useState(null);

  const detail = useRef(null);

  const shown = problems.filter((problem) => {
    const matchesFilter =
      filter === "All" || problem.area === filter;

    const searchableText = `
      ${problem.title}
      ${problem.short}
      ${problem.example}
      ${problem.term}
    `.toLowerCase();

    return (
      matchesFilter &&
      searchableText.includes(query.toLowerCase())
    );
  });

  function selectProblem(problem) {
    setSelected(problem);

    requestAnimationFrame(() => {
      detail.current?.focus();

      detail.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }

  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">
          The everyday problem library
        </p>

        <h1>Does this sound familiar?</h1>

        <p>
          Find a situation close to yours. Learn what the Act says,
          in ordinary language.
        </p>
      </div>

      <div className="library-controls">
        <label className="search">
          <Icon name="search" />

          <input
            type="search"
            aria-label="Search common problems"
            placeholder="Search: repair, price, unsafe…"
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
          />
        </label>

        <div
          className="filters"
          aria-label="Filter problems"
        >
          {[
            "All",
            "Shopping",
            "Services",
            "Payments",
            "Safety",
          ].map((filterName) => (
            <button
              type="button"
              key={filterName}
              aria-pressed={filterName === filter}
              className={
                filterName === filter ? "active" : ""
              }
              onClick={() => setFilter(filterName)}
            >
              {filterName}
            </button>
          ))}
        </div>
      </div>

      <p
        className="small muted"
        role="status"
      >
        {shown.length}{" "}
        {shown.length === 1 ? "situation" : "situations"} to
        explore
      </p>

      <div className="problem-grid">
        {shown.map((problem) => (
          <button
            type="button"
            className={`problem-card ${
              selected?.id === problem.id ? "selected" : ""
            }`}
            aria-pressed={selected?.id === problem.id}
            onClick={() => selectProblem(problem)}
            key={problem.id}
          >
            <div className="card-top">
              <span className="icon-box">
                <Icon
                  name={problem.icon}
                  size={26}
                />
              </span>

              <span className="tag">
                {problem.area}
              </span>
            </div>

            <h2>{problem.title}</h2>

            <p>{problem.short}</p>

            <div className="example">
              “{problem.example}”
            </div>

            <span className="card-link">
              Understand this situation
              <Icon name="arrow" size={19} />
            </span>
          </button>
        ))}
      </div>

      {!shown.length && (
        <div className="empty">
          <h2>No matching situations</h2>

          <p>
            Try a simpler word or browse all topics.
          </p>

          <button
            type="button"
            className="button secondary"
            onClick={() => {
              setQuery("");
              setFilter("All");
            }}
          >
            Show all situations
          </button>
        </div>
      )}

      {selected && (
        <div
          className="result-anchor"
          tabIndex={-1}
          ref={detail}
        >
          <ProblemDetail problem={selected} />
        </div>
      )}

      <div className="quiet-note">
        <Icon name="book" />

        <p>
          Not every difficulty is a consumer-law issue. These examples
          help you recognise topics; they do not decide your case.
        </p>
      </div>
    </>
  );
}