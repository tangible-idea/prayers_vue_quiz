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

    <!-- Quiz Result Popup -->
    <div v-if="showPopup" class="overlay">
      <div class="popup">
        <h3 v-if="isCorrect">🎉 Congratulations! You answered correctly! 🎉</h3>
        <h3 v-else>❌ Wrong answer. Better luck next time! ❌</h3>
        <!-- Display Reward or Users based on correctness -->
        <div v-if="isCorrect">
          <p>Here are the users:</p>
          <ul>
            <li v-for="user in users" :key="user.sender_key">
              <img :src="user.image" alt="User Image" class="user-image" />
              <strong>{{ user.sender }}</strong> - {{ user.room_tag }}
            </li>
          </ul>
        </div>
        <button @click="closePopup" class="close-button">Close</button>
      </div>
    </div>

    <!-- Error Popup -->
    <div v-if="showErrorPopup" class="overlay">
      <div class="popup">
        <h3>⚠️ Error ⚠️</h3>
        <p>{{ errorMessage }}</p>
        <button @click="closeErrorPopup" class="close-button">Close</button>
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
    const showPopup = ref(false); // Controls the quiz result popup visibility
    const isCorrect = ref(false); // Tracks if the user's answer is correct
    const users = ref([]); // Stores fetched users

    // State for Error Popup
    const showErrorPopup = ref(false);
    const errorMessage = ref("");

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

        // Check for 'room_tag'
        if (!data.room_tag) {
          throw new Error("Missing 'room_tag' parameter.");
        }else{
          localStorage.setItem("room_tag", data.room_tag);
        }

        return data; // Return the parsed object
      } catch (err) {
        console.error("Error decoding Base64 JSON data:", err);
        // Set error message and show error popup
        errorMessage.value = err.message;
        showErrorPopup.value = true;
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
          // Handle fetch error by showing error popup
          errorMessage.value = "Failed to fetch quizzes. Please try again later.";
          showErrorPopup.value = true;
        } else if (data && data.length > 0) {
          // Randomly pick one quiz from the fetched data
          const randomQuiz = data[Math.floor(Math.random() * data.length)];
          console.log("Randomly picked quiz:", randomQuiz);

          quizzes.value = [randomQuiz]; // Set the random quiz in the reactive state
        } else {
          console.warn("No quizzes found for the given type.");
          // Handle no quizzes found by showing error popup
          errorMessage.value = "No quizzes available for the provided type.";
          showErrorPopup.value = true;
        }
      } catch (err) {
        console.error("Unexpected error fetching quizzes:", err);
        // Handle unexpected errors
        errorMessage.value = "An unexpected error occurred. Please try again later.";
        showErrorPopup.value = true;
      }
    };

    // Const Arrow Function to Fetch Users from 'kakao_profile' Table
    const getUsers = async () => {
      console.log("Fetching users from 'kakao_profile' table...");
      try {
        const roomTag= localStorage.getItem("room_tag"); // get room_tag from Localstorage.

        const { data, error } = await supabase
          .from("kakao_profile")
          .select("room_tag, sender_key, image, sender")
          .eq('room_tag', roomTag);

        if (error) {
          console.error("Error fetching users:", error);
          // Handle fetch error by showing error popup
          errorMessage.value = "Failed to fetch users. Please try again later.";
          showErrorPopup.value = true;
          return [];
        }

        console.log("Fetched Users:", data);
        return data;
      } catch (err) {
        console.error("Unexpected error fetching users:", err);
        // Handle unexpected errors
        errorMessage.value = "An unexpected error occurred while fetching users.";
        showErrorPopup.value = true;
        return [];
      }
    };

    // Submit Answer
    const submitAnswer = async (quizId, answer) => {
      console.log("Submitting answer for quiz ID:", quizId);
      console.log("Selected answer:", answer);
      isAnswering.value = true;

      const quiz = quizzes.value.find((q) => q.id === quizId);

      // Check if the answer is correct
      if (quiz.answer && quiz.answer.includes(answer)) {
        console.log("Correct answer!");
        isCorrect.value = true;
        // Instead of awarding points, fetch users
        const fetchedUsers = await getUsers();
        users.value = fetchedUsers;
      } else {
        console.log("Wrong answer!");
        isCorrect.value = false;
        // Optionally, you can handle rewards or other logic for incorrect answers
      }

      // Show the popup
      showPopup.value = true;

      // Simulate delay for submission
      setTimeout(() => {
        isAnswering.value = false;
      }, 1000);
    };

    // Close Quiz Result Popup
    const closePopup = () => {
      showPopup.value = false;
    };

    // Close Error Popup
    const closeErrorPopup = () => {
      showErrorPopup.value = false;
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
        } else if (decoded === null) {
          // decodeBase64Data handles error popups, so just stop here
          quizStarted.value = false; // Revert quizStarted if decoding failed
        } else {
          console.error("Invalid Base64 string or missing type.");
          // Handle invalid type
          errorMessage.value = "Invalid quiz type provided.";
          showErrorPopup.value = true;
          quizStarted.value = false; // Revert quizStarted
        }
      } else {
        console.warn("No Base64 string provided in the URL.");
        // Handle missing Base64 string
        errorMessage.value = "No quiz data provided.";
        showErrorPopup.value = true;
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
      closeErrorPopup,
      showPopup,
      isCorrect,
      users,
      showErrorPopup,
      errorMessage,
    };
  },
};
</script>

<style>
/* General Styles */
body {
  font-family: 'Arial', sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f9f9f9;
  color: #333;
}

h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #555;
}

button {
  cursor: pointer;
  transition: all 0.3s ease;
}

/* Combobox Section */
.combo-section {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin: 20px;
  text-align: center;
}

/* Updated Combobox Styles */
.bible-combobox {
  width: 60%;
  padding: 12px 15px;
  margin: 15px 0;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
  outline: none;
  background-color: #ffffff; /* Light background for better readability */
  color: #333; /* Dark text for good contrast */
  transition: border-color 0.3s ease;
}

.bible-combobox:focus {
  border-color: #007bff; /* Highlight border on focus */
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5); /* Subtle focus glow */
}

.bible-combobox option {
  color: #333; /* Ensure options are readable as well */
  background-color: #ffffff; /* Keep the background consistent */
}

/* Buttons */
.submit-button,
.option-button,
.start-button,
.close-button {
  background-color: #007bff;
  color: #ffffff;
  border: none;
  padding: 12px 20px;
  margin: 10px;
  border-radius: 5px;
  font-size: 16px;
  font-weight: bold;
}

.submit-button:hover,
.option-button:hover,
.start-button:hover,
.close-button:hover {
  background-color: #0056b3;
}

.submit-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* Overlay (Popup Background) */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

/* Popup Styles */
.popup {
  background-color: #ffffff;
  padding: 30px;
  border-radius: 15px;
  text-align: center;
  animation: scaleUp 0.4s ease-out;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 500px;
}

.popup h3 {
  font-size: 1.8rem;
  margin-bottom: 15px;
  color: #333;
}

.popup p {
  font-size: 1rem;
  color: #666;
  margin-bottom: 20px;
}

.close-button {
  background-color: #007bff;
  color: #ffffff;
  padding: 10px 25px;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

.close-button:hover {
  background-color: #0056b3;
}

/* Animations */
@keyframes scaleUp {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* Start Screen */
.start-screen {
  text-align: center;
  padding: 50px;
  background-color: #ffffff;
  border-radius: 10px;
  margin: 20px auto;
  max-width: 600px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.start-button {
  background-color: #28a745;
  color: #ffffff;
  border: none;
  padding: 15px 25px;
  border-radius: 5px;
  font-size: 1.2rem;
  transition: background-color 0.3s ease;
}

.start-button:hover {
  background-color: #218838;
}

/* Question Section */
.question-section {
  padding: 20px;
  margin: 10px auto;
  max-width: 700px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.question {
  font-size: 1.2rem;
  margin-bottom: 20px;
  color: #444;
}

.option-button {
  background-color: #007bff;
  color: #ffffff;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  margin: 5px;
  transition: background-color 0.3s ease;
}

.option-button:hover {
  background-color: #0056b3;
}

.option-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* User List Styles */
.user-image {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
  vertical-align: middle;
}

/* Error Popup Specific Styles */
.popup h3:nth-of-type(1) {
  color: #e74c3c; /* Red color for error */
}

.popup p {
  color: #333; /* Darker text for better readability */
}
</style>