export const ACT_URL =
  "https://www.indiacode.nic.in/handle/123456789/15276?view_type=browse";

export const RIGHTS_URL =
  "https://consumerhelpline.gov.in/";

export const FAQ_URL =
  "https://www.consumerhelpline.gov.in/public/index.php/knowledgebasedetails/Consumer%20Protection%20Act%202019";

export const problems = [
  {
    id: "product",
    icon: "box",
    title: "Something I bought is faulty",
    area: "Shopping",
    short: "A damaged item or a product that does not work.",
    example: "My new mixer stopped working after two days.",
    words: [
      "broken",
      "faulty",
      "damaged",
      "defective",
      "not working",
      "stopped working",
      "തകരാർ",
      "കേടായ",
      "പ്രവർത്തിക്കുന്നില്ല",
    ],
    section: "2(10)",
    term: "Defect",
    explanation:
      "A product may have a defect when its quality or standard falls short of what the law, agreement or seller requires.",
    check:
      "What was promised, what went wrong, and how was the item used?",
    records: [
      "Purchase receipt or order confirmation",
      "Photos of the fault",
      "Warranty and product description",
    ],
  },

  {
    id: "service",
    icon: "tools",
    title: "A service was not done properly",
    area: "Services",
    short: "An incomplete repair or a paid service that fell short.",
    example:
      "I paid for a repair, but the promised work was not completed.",
    words: [
      "repair",
      "service",
      "paid",
      "delay",
      "delivery",
      "റിപ്പയർ",
      "സേവനം",
      "വൈകി",
    ],
    section: "2(11)",
    term: "Deficiency in service",
    explanation:
      "A service may be deficient when its performance falls short of a legal requirement or an agreed commitment.",
    check:
      "What service was agreed, when was it due, and what was actually provided?",
    records: [
      "Service bill",
      "Written promise or booking details",
      "Messages showing what happened",
    ],
  },

  {
    id: "advert",
    icon: "eye",
    title: "An advertisement misled me",
    area: "Shopping",
    short: "An important claim or promise turned out to be false.",
    example:
      "The advertisement promised a feature the product does not have.",
    words: [
      "advert",
      "promise",
      "fake",
      "misleading",
      "feature",
      "പരസ്യം",
      "വ്യാജ",
    ],
    section: "2(28)",
    term: "Misleading advertisement",
    explanation:
      "An advertisement may mislead through false claims or by hiding important information.",
    check:
      "Keep the exact claim and compare it with the product or service received.",
    records: [
      "Screenshot of the advertisement",
      "Product description",
      "Receipt and relevant messages",
    ],
  },

  {
    id: "price",
    icon: "receipt",
    title: "I was charged more than agreed",
    area: "Payments",
    short:
      "The amount on the bill differs from the displayed or agreed price.",
    example:
      "The shop charged more than the price printed on the package.",
    words: [
      "charged",
      "price",
      "bill",
      "mrp",
      "overcharge",
      "വില",
      "പണം",
      "ബിൽ",
    ],
    section: "2(6)(iv)",
    term: "Excess price",
    explanation:
      "Charging above a legally fixed, displayed or agreed price is one ground recognised in the Act's definition of a complaint.",
    check:
      "Compare the final bill with the applicable displayed or agreed price and disclosed charges.",
    records: [
      "Final bill",
      "Photo of the displayed price",
      "Booking or order price",
    ],
  },

  {
    id: "safety",
    icon: "shield",
    title: "A product seems unsafe",
    area: "Safety",
    short: "A purchase creates a risk to health or property.",
    example: "My charger sparks when it is plugged in.",
    words: [
      "unsafe",
      "spark",
      "burn",
      "injury",
      "expired",
      "അപകട",
      "തീ",
      "കാലാവധി",
    ],
    section: "2(9)(i)",
    term: "Right to safety",
    explanation:
      "Consumer rights include protection against goods and services that are hazardous to life or property.",
    check:
      "Stop using a potentially dangerous product. If there is immediate danger, prioritise safety and appropriate emergency help.",
    records: [
      "Product and packaging details",
      "Photos taken safely",
      "Receipt and any incident records",
    ],
  },

  {
    id: "terms",
    icon: "document",
    title: "The terms seem unfair",
    area: "Payments",
    short: "An excessive penalty or an unreasonable condition.",
    example:
      "The agreement asks for a penalty far larger than the seller's loss.",
    words: [
      "contract",
      "penalty",
      "deposit",
      "condition",
      "terms",
      "കരാർ",
      "പിഴ",
    ],
    section: "2(46)",
    term: "Unfair contract",
    explanation:
      "Certain contract terms that significantly disadvantage a consumer may fall within the Act's definition of an unfair contract.",
    check:
      "The full agreement and circumstances matter; an unwanted term is not automatically unlawful.",
    records: [
      "Full agreement",
      "Details of the disputed condition",
      "Bills and related correspondence",
    ],
  },
];

export const rights = [
  {
    icon: "shield",
    title: "Be safe",
    official: "Right to safety",
    section: "2(9)(i)",
    text: "Protection from goods and services that put life or property at risk.",
    example:
      "An appliance should not expose you to an avoidable electrical hazard.",
  },

  {
    icon: "eye",
    title: "Know what you are buying",
    official: "Right to information",
    section: "2(9)(ii)",
    text: "Know the price, quantity, quality and other important details.",
    example:
      "Read the weight, price and relevant product information before paying.",
  },

  {
    icon: "grid",
    title: "Have a choice",
    official: "Right to choose",
    section: "2(9)(iii)",
    text:
      "Access to different goods and services at competitive prices, wherever possible.",
    example: "Compare available options before choosing a service.",
  },

  {
    icon: "voice",
    title: "Be heard",
    official: "Right to be heard",
    section: "2(9)(iv)",
    text:
      "Your consumer interests should receive consideration at the appropriate forum.",
    example: "You can raise a concern about a purchase.",
  },

  {
    icon: "balance",
    title: "Seek a remedy",
    official: "Right to seek redressal",
    section: "2(9)(v)",
    text:
      "Seek redress against unfair practices or exploitation.",
    example:
      "A remedy depends on the facts; a refund is not automatic in every case.",
  },

  {
    icon: "book",
    title: "Understand your rights",
    official: "Right to consumer awareness",
    section: "2(9)(vi)",
    text:
      "Learn how to make informed consumer decisions.",
    example:
      "Understanding a warranty helps you know what was promised.",
  },
];

export function suggestTopics(text) {
  const value = text.toLowerCase();

  return problems.filter((problem) =>
    problem.words.some((word) => value.includes(word)),
  );
}