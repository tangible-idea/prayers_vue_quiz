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

// Supabase Client Initialization
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

export default {
  setup() {
    // Reactive State
    const quizzes = ref([]);
    const isAnswering = ref(false);
    const quizStarted = ref(false);

    // Helper: Decode Base64 string to retrieve quiz data (JSON format)
    const decodeBase64Data = (base64String) => {
      console.log('Decoding Base64 string:', base64String);
      try {
        const decodedString = atob(base64String); // Decode Base64 string
        console.log('Decoded string:', decodedString);

        // Parse JSON string into an object
        const data = JSON.parse(decodedString);
        console.log('Decoded Data (JSON):', data);
        return data; // Return the parsed object
      } catch (err) {
        console.error('Error decoding Base64 JSON data:', err);
        return null;
      }
    };

    // Fetch Quizzes Based on Decoded IDs
    const fetchQuizById = async (id) => {
      console.log('Fetching quizzes for ID:', id);
      try {
        let query = supabase.from('quiz').select('*'); // Use the correct table name
        if (id) {
          query = query.eq('id', id); // Query specific quiz by ID
        }
        const { data, error } = await query;

        if (error) {
          console.error('Error fetching quizzes:', error);
          return;
        }

        console.log('Fetched quizzes:', data);
        quizzes.value = data; // Populate quizzes with fetched data
      } catch (err) {
        console.error('Unexpected error fetching quizzes:', err);
      }
    };  

    // Fetch a Random Quiz Based on type
    const fetchQuizByType = async (type) => {
      console.log('Fetching a random quiz for type:', type);
      try {
        const { data, error } = await supabase
          .from('quiz')
          .select('*')
          .eq('type', type);

        if (error) {
          console.error('Error fetching quizzes:', error);
        } else {
          const randomQuiz = data[Math.floor(Math.random() * data.length)];
          console.log('Fetched a random quiz:', randomQuiz);
          quizzes.value = [randomQuiz]; // Populate quizzes with the single fetched quiz
        }
      } catch (err) {
        console.error('Unexpected error fetching a random quiz:', err);
      }
    };

    // Start Quiz
    const startQuiz = async () => {
      console.log('Starting quiz...');
      quizStarted.value = true; // Set quizStarted to true

      // Extract Base64-encoded data from the URL (path or query string)
      const base64String = window.location.pathname.split('/').pop(); // Extract the last part of the URL
      console.log('Base64 String from URL:', base64String);

      if (base64String) {
        const decodedData = decodeBase64Data(base64String); // Decode Base64 string
        if(decodedData) {
          console.log('Decoded Data2:', decodedData);
          if(decodedData.id) {
              await fetchQuizById(decodedData.id); // Fetch quizzes based on the decoded ID
          }else if(decodedData.type) {
              console.log('Fetching quizzes for type:', decodedData.type);
              await fetchQuizByType(decodedData.type); // Fetch quizzes based on the decoded type
          }
        } else {
          console.error('Invalid or missing ID in decoded data.');
        }
      } else {
        console.warn('No Base64 string provided in the URL.');
      }
    };

    // Handle Answer Selection
    const selectAnswer = (option) => {
      console.log('Selected answer:', option);
      // Add logic to handle the answer selection
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
