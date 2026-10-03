const MAX_UPLOAD_BYTES = 4 * 1024 * 1024;
const QUEUE_KEY = "fieldnote-scheduled-posts";

const form = document.querySelector("#generate-form");
const fileInput = document.querySelector("#pdf-files");
const fileList = document.querySelector("#file-list");
const dropzone = document.querySelector("#dropzone");
const topicInput = document.querySelector("#topic");
const contentInput = document.querySelector("#content");
const tweetInput = document.querySelector("#tweet");
const tweetCount = document.querySelector("#tweet-count");
const generateButton = document.querySelector("#generate-button");
const formStatus = document.querySelector("#form-status");
const resultState = document.querySelector("#result-state");
const xLink = document.querySelector("#x-link");
const scheduleForm = document.querySelector("#schedule-form");
const scheduleDate = document.querySelector("#schedule-date");
const scheduleStatus = document.querySelector("#schedule-status");
const queueElement = document.querySelector("#queue");

function setStatus(element, message, kind = "") {
  element.textContent = message;
  element.className = `form-status${kind ? ` is-${kind}` : ""}`;
}

function formatSize(size) {
  return size < 1024 * 1024
    ? `${Math.max(1, Math.round(size / 1024))} KB`
    : `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function selectedFiles() {
  return [...fileInput.files];
}

function renderFiles() {
  fileList.replaceChildren();
  for (const file of selectedFiles()) {
    const item = document.createElement("li");
    const name = document.createElement("strong");
    const size = document.createElement("span");
    item.className = "file-item";
    name.textContent = file.name;
    size.textContent = formatSize(file.size);
    item.append(name, size);
    fileList.append(item);
  }
  dropzone.querySelector(".drop-title").textContent = fileInput.files.length
    ? `${fileInput.files.length} PDF${fileInput.files.length === 1 ? "" : "s"} selected`
    : "Choose PDF files";
}

function makeShortPost(text, limit = 280) {
  const compact = text.replace(/\s+/g, " ").trim();
  if (compact.length <= limit) return compact;
  const shortened = compact.slice(0, limit - 1);
  const lastSpace = shortened.lastIndexOf(" ");
  return `${shortened.slice(0, lastSpace > 0 ? lastSpace : limit - 1).trimEnd()}…`;
}

function updateTweetLink() {
  const tweet = tweetInput.value;
  tweetCount.textContent = `${tweet.length} / 280`;
  tweetCount.classList.toggle("is-long", tweet.length > 280);
  if (!tweet.trim() || tweet.length > 280) {
    xLink.href = "#";
    xLink.classList.add("is-disabled");
    xLink.setAttribute("aria-disabled", "true");
    return;
  }
  xLink.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(tweet)}`;
  xLink.classList.remove("is-disabled");
  xLink.setAttribute("aria-disabled", "false");
}

function getQueue() {
  try {
    const posts = JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]");
    return Array.isArray(posts) ? posts : [];
  } catch {
    return [];
  }
}

function saveQueue(posts) {
  localStorage.setItem(QUEUE_KEY, JSON.stringify(posts));
}

function renderQueue() {
  const posts = getQueue();
  queueElement.replaceChildren();
  if (!posts.length) {
    const empty = document.createElement("p");
    empty.className = "queue-empty";
    empty.textContent = "Nothing scheduled yet.";
    queueElement.append(empty);
    return;
  }

  for (const post of posts) {
    const item = document.createElement("article");
    const details = document.createElement("div");
    const meta = document.createElement("div");
    const date = document.createElement("strong");
    const status = document.createElement("span");
    const copy = document.createElement("div");
    const actions = document.createElement("div");
    const shortPost = makeShortPost(post.content);
    const due = post.status === "Scheduled" && new Date(post.date).getTime() <= Date.now();

    item.className = `queue-item${due ? " is-due" : ""}${post.status === "Posted" ? " is-posted" : ""}`;
    item.dataset.id = post.id;
    meta.className = "queue-meta";
    date.textContent = new Date(post.date).toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
    status.textContent = post.status === "Posted" ? "Posted" : due ? "Due now" : "Scheduled";
    copy.className = "queue-copy";
    copy.textContent = post.content;
    actions.className = "queue-actions";
    meta.append(date, status);
    details.append(meta, copy);

    if (post.status === "Scheduled") {
      const postLink = document.createElement("a");
      postLink.className = "post-link";
      postLink.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shortPost)}`;
      postLink.target = "_blank";
      postLink.rel = "noopener noreferrer";
      postLink.textContent = "Open X";
      postLink.setAttribute("aria-label", `Open post scheduled for ${date.textContent} on X`);
      const markButton = document.createElement("button");
      markButton.type = "button";
      markButton.dataset.action = "posted";
      markButton.textContent = "Mark posted";
      actions.append(postLink, markButton);
    } else {
      const removeButton = document.createElement("button");
      removeButton.type = "button";
      removeButton.dataset.action = "remove";
      removeButton.textContent = "Remove";
      actions.append(removeButton);
    }

    item.append(details, actions);
    queueElement.append(item);
  }
}

fileInput.addEventListener("change", renderFiles);

for (const eventName of ["dragenter", "dragover"]) {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add("is-over");
  });
}

for (const eventName of ["dragleave", "drop"]) {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-over");
  });
}

dropzone.addEventListener("drop", (event) => {
  const files = [...(event.dataTransfer?.files || [])].filter((file) =>
    file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")
  );
  if (!files.length) {
    setStatus(formStatus, "Choose one or more PDF files.", "error");
    return;
  }
  const transfer = new DataTransfer();
  for (const file of files) transfer.items.add(file);
  fileInput.files = transfer.files;
  renderFiles();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const files = selectedFiles();
  const totalSize = files.reduce((sum, file) => sum + file.size, 0);
  if (!files.length) {
    setStatus(formStatus, "Upload at least one research PDF.", "error");
    return;
  }
  if (totalSize > MAX_UPLOAD_BYTES) {
    setStatus(formStatus, "PDF files must total less than 4 MB.", "error");
    return;
  }
  if (!topicInput.value.trim()) {
    setStatus(formStatus, "Add a topic to continue.", "error");
    return;
  }

  const payload = new FormData();
  payload.append("topic", topicInput.value.trim());
  for (const file of files) payload.append("pdfs", file, file.name);

  generateButton.disabled = true;
  generateButton.querySelector("span").textContent = "Reading your research...";
  resultState.textContent = "Working from your source";
  setStatus(formStatus, "The research agents are preparing a draft.");

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      body: payload,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Generation failed.");
    contentInput.value = data.content || "";
    tweetInput.value = makeShortPost(contentInput.value);
    updateTweetLink();
    resultState.textContent = "Draft ready to review";
    setStatus(formStatus, "Draft generated. Review it before sharing.", "success");
    contentInput.focus();
  } catch (error) {
    resultState.textContent = "Generation needs attention";
    setStatus(formStatus, error.message || "Could not reach the generation service.", "error");
  } finally {
    generateButton.disabled = false;
    generateButton.querySelector("span").textContent = "Generate content";
  }
});

contentInput.addEventListener("input", () => {
  tweetInput.value = makeShortPost(contentInput.value);
  updateTweetLink();
});
tweetInput.addEventListener("input", updateTweetLink);

scheduleForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const content = contentInput.value.trim();
  const date = new Date(scheduleDate.value);
  if (!content) {
    setStatus(scheduleStatus, "Generate or write content before scheduling it.", "error");
    return;
  }
  if (!scheduleDate.value || Number.isNaN(date.getTime())) {
    setStatus(scheduleStatus, "Choose a valid date and time.", "error");
    return;
  }
  const posts = getQueue();
  posts.unshift({ id: crypto.randomUUID(), date: date.toISOString(), content, status: "Scheduled" });
  try {
    saveQueue(posts);
    renderQueue();
    setStatus(scheduleStatus, "Added to this browser's queue.", "success");
  } catch {
    setStatus(scheduleStatus, "Browser storage is unavailable or full.", "error");
  }
});

queueElement.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const item = button.closest(".queue-item");
  const posts = getQueue();
  const post = posts.find((entry) => entry.id === item.dataset.id);
  if (!post) return;
  if (button.dataset.action === "posted") post.status = "Posted";
  if (button.dataset.action === "remove") {
    saveQueue(posts.filter((entry) => entry.id !== post.id));
  } else {
    saveQueue(posts);
  }
  renderQueue();
});

renderFiles();
renderQueue();
updateTweetLink();
window.setInterval(renderQueue, 30_000);