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
          <!-- If the quiz type is 'bible_verse', show a combobox -->
          <div v-if="quiz.type === 'bible_verse'" class="combo-section">
            <select v-model="selectedAnswer" class="bible-combobox">
              <option disabled value="">Select a Bible Book</option>
              <option v-for="(book, index) in bibleBooks" :key="index" :value="book">
                {{ book }}
              </option>
            </select>
            <button
              @click="submitAnswer(quiz.id, selectedAnswer)"
              class="submit-button"
              :disabled="!selectedAnswer || isAnswering"
            >
              Submit Answer
            </button>
          </div>

          <!-- If the quiz type is NOT 'bible_verse', show normal answer buttons -->
          <div v-else>
            <button
              v-for="(option, index) in quiz.options"
              :key="index"
              @click="submitAnswer(quiz.id, option)"
              class="option-button"
              :disabled="isAnswering"
            >
              {{ option }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Popup Section -->
    <div v-if="showPopup" class="overlay">
      <div class="popup">
        <h3 v-if="isCorrect">🎉 Congratulations! You answered correctly! 🎉</h3>
        <h3 v-else>❌ Wrong answer. Better luck next time! ❌</h3>
        <p v-if="isCorrect">Your reward: {{ reward }}</p>
        <button @click="closePopup" class="close-button">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import { createClient } from "@supabase/supabase-js";
import { ref } from "vue";

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
    const selectedAnswer = ref(""); // Stores the selected answer for bible_verse quizzes
    const decodedData = ref({}); // Decoded data from Base64
    const showPopup = ref(false); // Controls the popup visibility
    const isCorrect = ref(false); // Tracks if the user's answer is correct
    const reward = ref(""); // Stores the reward message
    const answeredQuizIds = ref(JSON.parse(localStorage.getItem("answeredQuizzes")) || []); // Track answered quizzes

    // Bible books in Korean
    const bibleBooks = ref([
      "창세기",
      "출애굽기",
      "레위기",
      "민수기",
      "신명기",
      "여호수아",
      "사사기",
      "룻기",
      "사무엘상",
      "사무엘하",
      "열왕기상",
      "열왕기하",
      "역대상",
      "역대하",
      "에스라",
      "느헤미야",
      "에스더",
      "욥기",
      "시편",
      "잠언",
      "전도서",
      "아가",
      "이사야",
      "예레미야",
      "예레미야애가",
      "에스겔",
      "다니엘",
      "호세아",
      "요엘",
      "아모스",
      "오바댜",
      "요나",
      "미가",
      "나훔",
      "하박국",
      "스바냐",
      "학개",
      "스가랴",
      "말라기",
      "마태복음",
      "마가복음",
      "누가복음",
      "요한복음",
      "사도행전",
      "로마서",
      "고린도전서",
      "고린도후서",
      "갈라디아서",
      "에베소서",
      "빌립보서",
      "골로새서",
      "데살로니가전서",
      "데살로니가후서",
      "디모데전서",
      "디모데후서",
      "디도서",
      "빌레몬서",
      "히브리서",
      "야고보서",
      "베드로전서",
      "베드로후서",
      "요한일서",
      "요한이서",
      "요한삼서",
      "유다서",
      "요한계시록",
    ]);

    // Helper: Decode Base64 string to retrieve quiz data (JSON format)
    const decodeBase64Data = (base64String) => {
      console.log("Decoding Base64 string:", base64String);
      try {
        const decodedString = atob(base64String); // Decode Base64 string
        console.log("Decoded string:", decodedString);

        // Parse JSON string into an object
        const data = JSON.parse(decodedString);
        console.log("Decoded Data (JSON):", data);
        return data; // Return the parsed object
      } catch (err) {
        console.error("Error decoding Base64 JSON data:", err);
        return null;
      }
    };

    // Fetch Quizzes Based on Decoded Data and Pick 1 Randomly
    const fetchQuizByType = async (type) => {
      console.log("Fetching quizzes for type:", type);
      try {
        const { data, error } = await supabase
          .from("quiz")
          .select("*")
          .eq("type", type); // Filter quizzes by the type

        if (error) {
          console.error("Error fetching quizzes:", error);
        } else if (data && data.length > 0) {
          // Randomly pick one quiz from the fetched data
          const randomQuiz = data[Math.floor(Math.random() * data.length)];
          console.log("Randomly picked quiz:", randomQuiz);

          quizzes.value = [randomQuiz]; // Set the random quiz in the reactive state
        } else {
          console.warn("No quizzes found for the given type.");
        }
      } catch (err) {
        console.error("Unexpected error fetching quizzes:", err);
      }
    };

    // Submit Answer
    const submitAnswer = (quizId, answer) => {
      console.log("Submitting answer for quiz ID:", quizId);
      console.log("Selected answer:", answer);
      isAnswering.value = true;

      // Check if the user has already answered this quiz
      if (answeredQuizIds.value.includes(quizId)) {
        alert("You have already answered this quiz!");
        return;
      }

      const quiz = quizzes.value.find((q) => q.id === quizId);

      // Check if the answer is correct
      if (quiz.answer && quiz.answer.includes(answer)) {
        console.log("Correct answer!");
        isCorrect.value = true;
        reward.value = "100 points"; // Example reward
      } else {
        console.log("Wrong answer!");
        isCorrect.value = false;
        reward.value = ""; // No reward
      }

      // Save answered quiz ID to prevent retrying
      answeredQuizIds.value.push(quizId);
      localStorage.setItem("answeredQuizzes", JSON.stringify(answeredQuizIds.value));

      // Show the popup
      showPopup.value = true;

      // Simulate delay for submission
      setTimeout(() => {
        isAnswering.value = false;
      }, 1000);
    };

    // Close Popup
    const closePopup = () => {
      showPopup.value = false;
    };

    // Start Quiz
    const startQuiz = async () => {
      console.log("Starting quiz...");
      quizStarted.value = true; // Set quizStarted to true

      // Extract Base64-encoded data from the URL (path or query string)
      const base64String = window.location.pathname.split("/").pop(); // Extract the last part of the URL
      console.log("Base64 String from URL:", base64String);

      if (base64String) {
        const decoded = decodeBase64Data(base64String); // Decode Base64 string
        if (decoded && decoded.type) {
          await fetchQuizByType(decoded.type); // Fetch quizzes based on the decoded type
        } else {
          console.error("Invalid Base64 string or missing type.");
        }
      } else {
        console.warn("No Base64 string provided in the URL.");
      }
    };

    return {
      quizzes,
      isAnswering,
      quizStarted,
      selectedAnswer,
      bibleBooks,
      startQuiz,
      submitAnswer,
      closePopup,
      showPopup,
      isCorrect,
      reward,
    };
  },
};
</script>

<style>
/* Add style for the combobox */
.combo-section {
  background-color: var(--white);
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin: 20px;
}

.bible-combobox {
  width: 50%;
  padding: 10px;
  margin: 10px 0;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.submit-button {
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

.submit-button:hover {
  background-color: var(--main-color);
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
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

.close-button {
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

.close-button:hover {
  background-color: var(--main-color);
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