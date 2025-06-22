// ========== Инициализация данных ==========
const gameEl = document.getElementById("game");
const playlistId = gameEl.dataset.playlistId;
const showWordFirst = gameEl.dataset.showWordFirst === "true";
const originalData = JSON.parse(document.getElementById("word-data").textContent);

let data = [];
let index = 0;
let flipped = false;
let known = 0;
let unknown = 0;
let skipped = 0;
let currentWord = null;
let gameFinished = false;
let wordStats = [];
let wrongWords = []; // Массив для хранения неправильных слов

// DOM элементы
const gameContent = document.getElementById("game-content");
const cardText = document.getElementById("card-text");
const currentIndex = document.getElementById("current-index");
const cardDetails = document.getElementById("card-details");
const cardContext = document.getElementById("card-context");
const actionButtons = document.getElementById("action-buttons");
const flipBtn = document.getElementById("flip-btn");
const flipText = document.getElementById("flip-text");
const detailsBtn = document.getElementById("details-btn");
const contextBtn = document.getElementById("context-btn");
const resultEl = document.getElementById("result");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");
const knownCount = document.getElementById("known-count");
const unknownCount = document.getElementById("unknown-count");
const skippedCount = document.getElementById("skipped-count");
const knownPercent = document.getElementById("known-percent");
const unknownPercent = document.getElementById("unknown-percent");
const skippedPercent = document.getElementById("skipped-percent");
const repeatMistakesBtn = document.getElementById("repeat-mistakes-btn");

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function startSession() {
  data = shuffle([...originalData]);
  index = 0;
  known = 0;
  unknown = 0;
  skipped = 0;
  flipped = false;
  gameFinished = false;
  wordStats = [];
  wrongWords = [];

  resultEl.style.display = "none";
  gameContent.style.display = "block";
  actionButtons.style.display = "none";
  cardDetails.style.display = "none";
  cardContext.style.display = "none";

  updateProgress();
  showCard();
}

function showCard() {
  if (gameFinished || index >= data.length) return;

  currentWord = data[index];
  currentIndex.textContent = index + 1;

  cardDetails.innerHTML = currentWord.details || "Описание отсутствует";
  cardContext.innerHTML = currentWord.context || "Пример отсутствует";

  cardDetails.style.display = "none";
  cardContext.style.display = "none";

  if (showWordFirst) {
    cardText.textContent = currentWord.word;
    flipped = false;
    flipText.textContent = "Показать перевод";
  } else {
    cardText.textContent = currentWord.translation;
    flipped = true;
    flipText.textContent = "Показать слово";
  }

  actionButtons.style.display = "block";
}

function toggleTranslation() {
  if (gameFinished) return;

  if (flipped) {
    cardText.textContent = currentWord.word;
    speak(currentWord.word);
    flipped = false;
    flipText.textContent = "Показать перевод";
    actionButtons.style.display = "none";
  } else {
    cardText.textContent = currentWord.translation;
    flipped = true;
    flipText.textContent = "Показать слово";
    actionButtons.style.display = "flex";
  }
}

function toggleDetails() {
  if (gameFinished) return;
  cardDetails.style.display = cardDetails.style.display === "none" ? "block" : "none";
}

function toggleContext() {
  if (gameFinished) return;
  cardContext.style.display = cardContext.style.display === "none" ? "block" : "none";
}

function markWord(isKnown) {
  if (gameFinished) return;

  if (isKnown) {
    known++;
  } else {
    unknown++;
    wrongWords.push(currentWord);
  }

  wordStats.push({
    word_id: currentWord.id,
    is_known: isKnown,
    playlist_id: playlistId
  });

  nextCard();
}

function skipWord() {
  if (gameFinished) return;
  skipped++;
  wrongWords.push(currentWord);
  nextCard();
}

function nextCard() {
  index++;
  updateProgress();
  if (index < data.length) {
    showCard();
  } else {
    finishGame();
  }
}

function updateProgress() {
  const progress = (index / data.length) * 100;
  progressBar.style.width = `${progress}%`;
  progressText.textContent = `${index}/${data.length}`;
}

function finishGame() {
  gameFinished = true;
  const total = known + unknown + skipped;
  const knownPct = total ? Math.round((known / total) * 100) : 0;
  const unknownPct = total ? Math.round((unknown / total) * 100) : 0;
  const skippedPct = total ? Math.round((skipped / total) * 100) : 0;

  knownCount.textContent = known;
  unknownCount.textContent = unknown;
  skippedCount.textContent = skipped;
  knownPercent.textContent = knownPct;
  unknownPercent.textContent = unknownPct;
  skippedPercent.textContent = skippedPct;

  repeatMistakesBtn.style.display = wrongWords.length > 0 ? "inline-block" : "none";
  gameContent.style.display = "none";
  resultEl.style.display = "block";

  sendStatistics();
}

function sendStatistics() {
  const csrfToken = getCookie("csrftoken");

  fetch("/results/save/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({
      playlist_id: playlistId,
      known: known,
      unknown: unknown,
      skipped: skipped,
    }),
  });

  if (wordStats.length > 0) {
    fetch("/results/save-word-results/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({
        word_results: wordStats
      }),
    });
  }
}

function restart() {
  startSession();
}

function repeatMistakes() {
  if (wrongWords.length === 0) return;

  data = shuffle([...wrongWords]);
  index = 0;
  known = 0;
  unknown = 0;
  skipped = 0;
  flipped = false;
  gameFinished = false;
  wordStats = [];
  wrongWords = [];

  resultEl.style.display = "none";
  gameContent.style.display = "block";
  actionButtons.style.display = "none";
  cardDetails.style.display = "none";
  cardContext.style.display = "none";

  updateProgress();
  showCard();
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

document.addEventListener("keydown", function(event) {
  if (gameFinished) return;

  switch(event.key) {
    case "ArrowRight": event.preventDefault(); markWord(true); break;
    case "ArrowLeft": event.preventDefault(); markWord(false); break;
    case "ArrowUp": event.preventDefault(); skipWord(); break;
    case "ArrowDown": event.preventDefault(); toggleDetails(); break;
    case " ": event.preventDefault(); toggleTranslation(); break;
  }
});

document.addEventListener("DOMContentLoaded", startSession);

function speak(text) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'de-DE';
    window.speechSynthesis.speak(utterance);
  } else {
    alert("Ваш браузер не поддерживает озвучивание.");
  }
}

function addToFavorites() {
  if (!currentWord || !currentWord.id) return;

  fetch(`/words/add-to-favorites/${currentWord.id}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      if(data.added) {
        showFavoriteMessage('Слово добавлено в избранное!');
      } else {
        showFavoriteMessage('Слово удалено из избранного!');
      }
    } else {
      showFavoriteMessage('Не удалось добавить слово в избранное.', true);
    }
  });
}

function showFavoriteMessage(text, isError = false) {
  const msg = document.getElementById('favorite-message');
  msg.textContent = text;
  msg.style.background = isError ? '#f44336' : '#4caf50';
  msg.style.display = 'block';
  msg.style.opacity = '1';

  setTimeout(() => {
    msg.style.transition = 'opacity 0.5s ease';
    msg.style.opacity = '0';
    setTimeout(() => {
      msg.style.display = 'none';
      msg.style.transition = '';
    }, 500);
  }, 3000);
}
