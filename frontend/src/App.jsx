import { useEffect, useRef, useState } from "react";
import Icon from "./components/Icon";
import Understand from "./pages/Understand";
import CommonProblems from "./pages/CommonProblems";
import YourRights from "./pages/YourRights";
import AboutAct from "./pages/AboutAct";

const pages = [
  {
    id: "start",
    name: "Understand a Problem",
  },
  {
    id: "problems",
    name: "Common Problems",
  },
  {
    id: "rights",
    name: "Your Basic Rights",
  },
  {
    id: "act",
    name: "About the Act",
  },
];

function getCurrentRoute() {
  const id = window.location.hash.slice(2);

  return pages.some((page) => page.id === id) ? id : "start";
}

function getPreference(key, fallback) {
  try {
    return localStorage.getItem(key) || fallback;
  } catch {
    return fallback;
  }
}

export default function App() {
  const [page, setPage] = useState(getCurrentRoute);

  const [size, setSize] = useState(() =>
    getPreference("compass-size", "standard"),
  );

  const [contrast, setContrast] = useState(
    () => getPreference("compass-contrast", "false") === "true",
  );

  const [draft, setDraft] = useState("");
  const [selected, setSelected] = useState(null);

  const mainRef = useRef(null);
  const firstLoad = useRef(true);

  useEffect(() => {
    function handleRouteChange() {
      if (window.location.hash.startsWith("#/")) {
        setPage(getCurrentRoute());
      }
    }

    window.addEventListener("hashchange", handleRouteChange);

    return () => {
      window.removeEventListener("hashchange", handleRouteChange);
    };
  }, []);

  useEffect(() => {
    const activePage = pages.find((item) => item.id === page);

    document.title = `${activePage.name} | Consumer Compass`;

    window.speechSynthesis?.cancel();

    if (firstLoad.current) {
      firstLoad.current = false;
      return;
    }

    window.scrollTo({
      top: 0,
      behavior: "instant",
    });

    mainRef.current?.focus({
      preventScroll: true,
    });
  }, [page]);

  useEffect(() => {
    document.documentElement.style.fontSize =
      size === "large" ? "20px" : "16px";

    try {
      localStorage.setItem("compass-size", size);
      localStorage.setItem("compass-contrast", String(contrast));
    } catch {
      // Local storage may be unavailable in private browsing.
    }
  }, [size, contrast]);

  return (
    <div className={contrast ? "app high-contrast" : "app"}>
      <a className="skip-link" href="#main">
        Skip to content
      </a>

      <div className="utility-bar">
       <div
           className="container utility-inner"
           style={{ justifyContent: "flex-end" }}
>
        

          <div className="access-controls">
            <span>Text size</span>

            <button
              type="button"
              aria-label="Standard text size"
              aria-pressed={size === "standard"}
              onClick={() => setSize("standard")}
            >
              A
            </button>

            <button
              type="button"
              aria-label="Larger text size"
              aria-pressed={size === "large"}
              onClick={() => setSize("large")}
            >
              A+
            </button>

            <button
              type="button"
              aria-pressed={contrast}
              onClick={() => setContrast((previous) => !previous)}
            >
              High contrast
            </button>
          </div>
        </div>
      </div>

      <header className="site-header">
        <div className="container header-inner">
          <a
            href="#/start"
            className="brand"
            aria-label="Consumer Compass home"
          >
            <span className="brand-icon">
              <Icon name="compass" size={30} />
            </span>

            <span>
              Consumer <b>Compass</b>
              <small>Your everyday rights guide</small>
            </span>
          </a>

          <nav aria-label="Main navigation">
            {pages.map((item) => (
              <a
                key={item.id}
                href={`#/${item.id}`}
                aria-current={page === item.id ? "page" : undefined}
              >
                {item.name}
              </a>
            ))}
          </nav>
        </div>
      </header>

      <main
        className="container"
        id="main"
        tabIndex={-1}
        ref={mainRef}
      >
        {page === "start" && (
          <Understand
            draft={draft}
            setDraft={setDraft}
            selected={selected}
            setSelected={setSelected}
          />
        )}

        {page === "problems" && <CommonProblems />}

        {page === "rights" && <YourRights />}

        {page === "act" && <AboutAct />}
      </main>

      <footer>
        <div className="container footer-inner">
          <div className="footer-brand">
            <Icon name="compass" />

            <strong>Consumer Compass</strong>

            <span>Clarity before your next step.</span>
          </div>

          <p>
            Independent educational guide · Consumer Protection Act, 2019
            <br />
            General information, not a legal decision.
          </p>

          <a href="#/act">About this guide ↗</a>
        </div>
      </footer>
    </div>
  );
}