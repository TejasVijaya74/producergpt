const ideaInput = document.querySelector("#movie-idea");
const generateButton = document.querySelector("#generate-button");
const requestStatus = document.querySelector("#request-status");
const runStatus = document.querySelector("#run-status");
const outputState = document.querySelector("#output-state");
const jsonOutput = document.querySelector("#json-output");
const serviceState = document.querySelector("#service-state span:last-child");
const stageElements = new Map(
  [...document.querySelectorAll("#agent-timeline li")].map((element) => [
    element.dataset.stage,
    element,
  ]),
);
const metricElements = [...document.querySelectorAll("#metrics-list dd")];

const stageOrder = ["research", "ceo", "planner", "creative", "studio", "copilot"];
const metricKeys = [
  "total_execution_time",
  "research_time",
  "ceo_time",
  "planner_time",
  "creative_pool_time",
];
const creativeAgentNames = [
  "Script Agent",
  "Storyboard Agent",
  "Dialogue Agent",
  "Music Agent",
  "Poster Agent",
];

let progressTimer;

function setStageState(stage, state, label) {
  const stageElement = stageElements.get(stage);
  if (!stageElement) {
    return;
  }

  stageElement.classList.remove("is-active", "is-complete", "is-failed");
  if (state) {
    stageElement.classList.add(`is-${state}`);
  }
  stageElement.querySelector(".stage-status").textContent = label;
}

function resetStages() {
  stageOrder.forEach((stage) => setStageState(stage, "", "Queued"));
}

function startProgressPreview() {
  let activeIndex = 0;
  setStageState(stageOrder[activeIndex], "active", "Running");

  progressTimer = window.setInterval(() => {
    if (activeIndex >= stageOrder.length - 1) {
      return;
    }
    setStageState(stageOrder[activeIndex], "complete", "Working");
    activeIndex += 1;
    setStageState(stageOrder[activeIndex], "active", "Running");
  }, 220);
}

function stopProgressPreview() {
  window.clearInterval(progressTimer);
  progressTimer = undefined;
}

function timelineStatus(entries, agentNames) {
  const matches = entries.filter((entry) => agentNames.includes(entry.agent));
  if (!matches.length) {
    return { state: "", label: "Queued" };
  }
  if (matches.some((entry) => entry.status === "failed")) {
    return { state: "failed", label: "Failed" };
  }
  if (matches.every((entry) => entry.status === "skipped")) {
    return { state: "", label: "Skipped" };
  }
  return { state: "complete", label: "Completed" };
}

function renderTimeline(entries = []) {
  const groups = {
    research: ["Research Agent"],
    ceo: ["CEO Agent"],
    planner: ["Planner Agent"],
    creative: creativeAgentNames,
    studio: ["Studio Agent"],
    copilot: ["Creator Copilot"],
  };

  Object.entries(groups).forEach(([stage, agentNames]) => {
    const { state, label } = timelineStatus(entries, agentNames);
    setStageState(stage, state, label);
  });
}

function renderMetrics(metrics = {}) {
  metricElements.forEach((element, index) => {
    element.textContent = metrics[metricKeys[index]] || "--";
  });
}

function renderResult(payload) {
  jsonOutput.textContent = JSON.stringify(payload, null, 2);
  renderTimeline(payload.execution_timeline);
  renderMetrics(payload.metrics);

  const workflow = payload.workflow || {};
  const status = workflow.status || "Completed";
  runStatus.textContent = status;
  runStatus.className = "run-status is-complete";
  outputState.textContent = status;
  outputState.className = "output-state is-complete";
  requestStatus.textContent = workflow.greenlight
    ? "Production package assembled."
    : "The project was not greenlighted.";
}

function renderError(message) {
  const activeStage = stageOrder.find((stage) =>
    stageElements.get(stage)?.classList.contains("is-active"),
  );
  if (activeStage) {
    setStageState(activeStage, "failed", "Failed");
  }

  jsonOutput.textContent = JSON.stringify({ error: message }, null, 2);
  runStatus.textContent = "Failed";
  runStatus.className = "run-status is-error";
  outputState.textContent = "Error";
  outputState.className = "output-state is-error";
  requestStatus.textContent = message;
}

function delay(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

async function generatePackage() {
  const idea = ideaInput.value.trim();
  if (idea.length < 10) {
    requestStatus.textContent = "Enter a movie idea with at least 10 characters.";
    ideaInput.focus();
    return;
  }

  generateButton.disabled = true;
  generateButton.classList.add("is-loading");
  serviceState.textContent = "Generating";
  requestStatus.textContent = "Autonomous workflow in progress.";
  runStatus.textContent = "Running";
  runStatus.className = "run-status is-running";
  outputState.textContent = "Generating";
  outputState.className = "output-state";
  resetStages();
  startProgressPreview();

  try {
    const request = fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idea }),
    });
    const [response] = await Promise.all([request, delay(1350)]);
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "The studio could not generate a package.");
    }

    renderResult(payload);
  } catch (error) {
    renderError(error instanceof Error ? error.message : "Unexpected generation failure.");
  } finally {
    stopProgressPreview();
    generateButton.disabled = false;
    generateButton.classList.remove("is-loading");
    serviceState.textContent = "Ready";
  }
}

generateButton.addEventListener("click", generatePackage);
ideaInput.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    generatePackage();
  }
});