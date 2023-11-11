import Heading from "@theme/Heading";
import clsx from "clsx";
import styles from "./styles.module.css";

const FeatureList = [
  {
    title: "Simple, Flexible Pricing",
    Svg: require("@site/static/img/undraw_docusaurus_mountain.svg").default,
    description: (
      <>
        YiVal carries industry leading standard s and practices to safe guard
        your valuable information.
      </>
    ),
  },
  {
    title: "Safety and Privacy",
    Svg: require("@site/static/img/undraw_docusaurus_tree.svg").default,
    description: (
      <>
        YiVal's team has its roots in health data and enforcing compliance of
        privacy measures. We use the latest standards and methods to keep your
        data safe.
      </>
    ),
  },
  {
    title: "Built-In Version Control",
    Svg: require("@site/static/img/undraw_docusaurus_react.svg").default,
    description: (
      <>
        YiVal keeps track of prompts, model versions, and performance as you
        work. It's git for GenAI, but you don't need to remember the command for
        rebasing.
      </>
    ),
  },
];

function Feature({ Svg, title, description }) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
