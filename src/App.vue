<template>
  <div id="app">
    <!-- Start Screen -->
    <div v-if="!quizStarted" class="start-screen">
      <h3>Today's Quiz</h3>
      <button @click="startQuiz" class="start-button">Start Quiz</button>
    </div>

    <!-- Quiz Section -->
    <div class="question-section" v-if="quizStarted && quizzes.length > 0">
      <div v-for="quiz in quizzes" :key="quiz.id">
        <p class="question">{{ quiz.question }}</p>
        <div class="options">
          <button
            v-for="(option, index) in quiz.options"
            :key="index"
            @click="selectAnswer(option)"
            class="option-button"
            :disabled="isAnswering"
          >
            {{ option }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { createClient } from '@supabase/supabase-js';
import { ref } from 'vue';

// Initialize Supabase client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

export default {
  setup() {
    // Reactive state
    const quizzes = ref([]); // List of quizzes
    const isAnswering = ref(false); // Tracks if a user is currently answering
    const quizStarted = ref(false); // Tracks if the quiz has started

    // Fetch quizzes from Supabase
    const fetchQuizzes = async () => {
      const { data, error } = await supabase.from('quiz').select('*');

      if (error) {
        console.error('Error fetching quizzes:', error);
        return;
      }

      // Populate quizzes with the fetched data
      if (data.length >= 3) {
        quizzes.value = data.slice(0, 3); // Limit to the first 3 quizzes
      } else {
        quizzes.value = data; // Use all available quizzes if less than 3
      }
    };

    // Start the quiz
    const startQuiz = async () => {
      quizStarted.value = true; // Set the `quizStarted` flag to true
      await fetchQuizzes(); // Fetch quizzes
    };

    // Handle selecting an answer
    const selectAnswer = (option) => {
      console.log('Selected answer:', option);
      // Additional logic for handling answers can go here
    };

    return {
      quizzes,
      isAnswering,
      quizStarted,
      startQuiz,
      selectAnswer,
    };
  },
};
</script>

<style>
/* 기존 스타일 유지 */
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 20px;
}

/* 색상 변수 */
:root {
  --main-color: #D2B48C;
  --secondary-color: #C1A378;
  --accent-color: #B08F68;
  --text-color: #333;
  --popup-bg: rgba(0, 0, 0, 0.5);
  --white: #fff;
  --light-bg: #f5f5dc;
}

/* 전반적인 스타일 */
#app {
  font-family: 'Arial', sans-serif;
  text-align: center;
  color: var(--text-color);
  min-height: 100vh;
  background-color: var(--light-bg);
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 시작 화면 및 완료 화면 */
.start-screen,
.completion-screen {
  background-color: var(--white);
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.start-button,
.option-button,
.close-button,
.restart-button {
  background-color: var(--secondary-color);
  color: var(--white);
  border: none;
  padding: 10px 20px;
  margin: 10px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.start-button:hover,
.option-button:hover,
.close-button:hover,
.restart-button:hover {
  background-color: var(--main-color);
}

/* 퀴즈 헤더 */
.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
  background-color: var(--accent-color);
  padding: 10px 20px;
  border-radius: 5px;
  color: var(--white);
}

.score {
  font-size: 18px;
}

/* 프로그레스바 */
.progress-bar-container {
  width: 100%;
  height: 10px;
  background-color: #ddd;
  position: fixed;
  top: 0;
  left: 0;
}

.progress-bar {
  height: 100%;
  background-color: var(--secondary-color);
  transition: width 0.1s linear;
}

/* 질문 섹션 */
.question-section {
  background-color: var(--white);
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin: 20px;
}

.question {
  font-size: 20px;
  margin-bottom: 20px;
}

.options {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.option-button {
  width: 80%;
  margin: 10px 0;
}

/* 오버레이 및 팝업 */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--popup-bg);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.popup {
  background-color: var(--white);
  padding: 30px;
  border-radius: 10px;
  text-align: center;
  animation: popin 0.5s ease-out;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes popin {
  from {
    transform: scale(0.5);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
