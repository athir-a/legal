import { ACT_URL, FAQ_URL } from "../data";
import Icon from "../components/Icon";

const topics = [
  [
    "Who is a consumer?",
    "A person buying goods or hiring services for payment, including approved users or beneficiaries. Resale and commercial use are generally excluded; goods used exclusively for a self-employed livelihood have a specific exception.",
    "2(7)",
  ],

  [
    "Does online shopping count?",
    "The definition includes online as well as offline transactions. Buying through a website does not by itself remove consumer protection.",
    "2(7)",
  ],

  [
    "What does the CCPA do?",
    "The Central Consumer Protection Authority addresses consumer-rights violations, unfair trade practices and misleading advertisements affecting consumers as a class.",
    "10 and 18",
  ],

  [
    "What are Consumer Commissions?",
    "The Act establishes District, State and National Commissions for consumer disputes. This guide explains the law; it does not file a case.",
    "28, 42 and 53",
  ],

  [
    "What is product liability?",
    "The Act has provisions for harm caused by defective products or related deficient services. Conditions and exceptions apply; damage only to the product itself is excluded from the defined harm.",
    "2(22), 82–87",
  ],

  [
    "What is mediation?",
    "Mediation is a process in which a mediator helps parties resolve a dispute. The Act provides a consumer mediation framework.",
    "74–81",
  ],
];

export default function AboutAct() {
  return (
    <>
      <section className="act-hero">
        <div>
          <p className="eyebrow">
            Meet the law behind your rights
          </p>

          <h1>
            The Consumer
            <br />
            Protection Act, 2019.
          </h1>

          <p className="lead">
            A law for the things we buy and the services we use.
            A framework to protect consumer interests and address disputes.
          </p>

          <a
            className="button primary"
            href={ACT_URL}
            target="_blank"
            rel="noreferrer"
          >
            Read the official Act
            <Icon name="arrow" size={20} />
          </a>
        </div>

        <div
          className="act-book"
          aria-hidden="true"
        >
          <Icon name="balance" size={48} />

          <span>
            UNDERSTANDING THE
          </span>

          <h2>
            Consumer
            <br />
            Protection
            <br />
            Act
          </h2>

          <strong>2019</strong>

          <div className="book-rule" />

          <small>
            A plain-language introduction
          </small>
        </div>
      </section>

      <div className="section-title">
        <div>
          <p className="eyebrow">
            The essentials
          </p>

          <h2>
            A few things worth knowing.
          </h2>
        </div>

        <span className="tag">
          Open any topic
        </span>
      </div>

      <div className="act-topics">
        {topics.map(([title, text, section], index) => (
          <details key={title}>
            <summary>
              <span className="topic-number">
                0{index + 1}
              </span>

              {title}

              <span className="plus">
                +
              </span>
            </summary>

            <div className="topic-body">
              <p>{text}</p>

              <a
                className="section-link"
                href={ACT_URL}
                target="_blank"
                rel="noreferrer"
              >
                Sections {section} · Official Act ↗
              </a>
            </div>
          </details>
        ))}
      </div>

      <section className="about-guide">
        <div>
          <p className="eyebrow">
            About Consumer Compass
          </p>

          <h2>
            Built for understanding.
          </h2>

          <p>
            An independent educational guide focused on the Consumer
            Protection Act, 2019. It is not a government website or a
            complaint-filing service.
          </p>
        </div>

        <div>
          <h3>
            How the problem guide works
          </h3>

          <p>
            You choose a situation, or use a short description to find
            suggested topics. Suggestions use a small keyword catalogue,
            including selected Malayalam words. They are not a legal
            assessment or a general translation service.
          </p>

          <h3>
            Your words stay in this session
          </h3>

          <p>
            This app does not upload or save your typed story. Voice
            recognition may use your browser provider’s online service.
            Only your text-size and contrast preferences are saved on this
            device.
          </p>
        </div>
      </section>

      <div className="source-panel">
        <Icon name="book" />

        <div>
          <h3>
            Go to the source
          </h3>

          <a
            href={ACT_URL}
            target="_blank"
            rel="noreferrer"
          >
            India Code: Consumer Protection Act, 2019 ↗
          </a>

          <a
            href={FAQ_URL}
            target="_blank"
            rel="noreferrer"
          >
            National Consumer Helpline: Act explained ↗
          </a>

          <p className="small muted">
            Learning content reviewed against these sources on 1 October
            2026. Read the official text for full conditions and amendments.
          </p>
        </div>
      </div>
    </>
  );
}