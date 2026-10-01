import { rights, ACT_URL, RIGHTS_URL } from "../data";
import Icon from "../components/Icon";
import ReadAloud from "../components/ReadAloud";

export default function YourRights() {
  const readingText = rights
    .map(
      (right) =>
        `${right.title}. ${right.text} ${right.example}`,
    )
    .join(" ");

  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">
          Your rights, made familiar
        </p>

        <h1>
          You are more than a customer.
          <br />
          <em>You are a consumer with rights.</em>
        </h1>

        <p>
          Six everyday protections. You don’t need a law degree to
          understand them.
        </p>

        <ReadAloud text={readingText} />
      </div>

      <div className="rights-grid">
        {rights.map((right, index) => (
          <article
            className="right-card"
            key={right.title}
          >
            <div className="card-top">
              <span className="icon-box">
                <Icon
                  name={right.icon}
                  size={27}
                />
              </span>

              <span className="big-number">
                0{index + 1}
              </span>
            </div>

            <span className="eyebrow">
              {right.official}
            </span>

            <h2>{right.title}</h2>

            <p>{right.text}</p>

            <details>
              <summary>
                An everyday example
              </summary>

              <p>{right.example}</p>
            </details>

            <a
              className="section-link"
              href={ACT_URL}
              target="_blank"
              rel="noreferrer"
            >
              Section {right.section} ↗
            </a>
          </article>
        ))}
      </div>

      <p className="small muted">
        Plain-language learning summaries.{" "}
        <a
          href={RIGHTS_URL}
          target="_blank"
          rel="noreferrer"
        >
          Read the National Consumer Helpline’s rights guide ↗
        </a>
      </p>
    </>
  );
}