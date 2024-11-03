<template>
  <div id="app">
    <!-- 시작 화면 -->
    <div v-if="!quizStarted" class="start-screen">
      <h1>오늘의 퀴즈</h1>
      <button @click="startQuiz" class="start-button">퀴즈 시작하기</button>
    </div>

    <!-- 퀴즈 화면 -->
    <div v-else class="quiz-container">
      <!-- 프로그레스바 타이머 -->
      <div class="progress-bar-container">
        <div
          class="progress-bar"
          :style="{ width: progressBarWidth + '%' }"
        ></div>
      </div>

      <!-- 헤더 -->
      <div class="quiz-header">
        <h2>레벨 {{ currentQuestion.level }}</h2>
        <div class="score">내 점수: {{ score }} 달란트</div>
      </div>

      <!-- 질문 섹션 -->
      <div class="question-section">
        <p class="question">{{ currentQuestion.question }}</p>
        <div class="options">
          <button
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            @click="selectAnswer(option)"
            class="option-button"
            :disabled="isAnswering"
          >
            {{ option }}
          </button>
        </div>
      </div>

      <!-- Dimm 처리 및 팝업 -->
      <div v-if="showPopup" class="overlay">
        <transition name="fade">
          <div class="popup">
            <p v-if="isCorrect">
              정답입니다! +{{ currentQuestion.talent }} 달란트를 획득했습니다.
            </p>
            <p v-else>
              오답입니다! 정답은 "{{ currentQuestion.answer }}" 입니다.
            </p>
            <button @click="closePopup" class="close-button">확인</button>
          </div>
        </transition>
      </div>

      <!-- 퀴즈 완료 화면 -->
      <div v-if="quizCompleted" class="overlay">
        <div class="completion-screen">
          <h2>퀴즈 완료!</h2>
          <p>최종 점수: {{ score }} 달란트</p>
          <button @click="resetQuiz" class="restart-button">다시 시작하기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';

export default {
  name: 'App',
  setup() {
    // 상태 관리
    const quizStarted = ref(false);
    const quizCompleted = ref(false);
    const questions = ref([]);
    const currentQuestionIndex = ref(0);
    const timer = ref(15);
    const timerInterval = ref(null);
    const score = ref(0);
    const showPopup = ref(false);
    const isCorrect = ref(false);
    const isAnswering = ref(false);
    const progressBarWidth = ref(100);
    const progressInterval = ref(null);

    // 현재 질문 계산
    const currentQuestion = computed(() => questions.value[currentQuestionIndex.value]);

    // 질문 가져오기
    const fetchQuestions = async () => {
      try {
        // API 요청: 각 레벨별로 하나씩 질문을 가져온다고 가정
        const levels = [1, 2, 3];
        const fetchedQuestions = [];

        for (const level of levels) {
          const response = await axios.get('https://aiconnect-fjptw3x2.b4a.run/bot/GPT-4o', {
            params: { request: `Generate a Bible quiz question for level ${level}. Include question, options, answer, and talent.` },
          });
          // API 응답 형식에 따라 처리 (예시)
          // { data: { question: '', options: [], answer: '', talent: 3, level: 1 } }
          if (response.data) {
            fetchedQuestions.push(response.data);
          }
        }

        questions.value = fetchedQuestions;
      } catch (error) {
        console.error('퀴즈 질문을 가져오는 중 오류 발생:', error);
        // 샘플 질문 사용
        questions.value = getSampleQuestions();
      }
    };

    // 샘플 질문 (API 실패 시)
    const getSampleQuestions = () => {
      return [
        {
          level: 1,
          question: '“여호와는 나의 목자시니 내게 부족함이 없으리로다.”',
          options: ['창세기', '시편', '이사야'],
          answer: '시편',
          talent: 3,
        },
        {
          level: 2,
          question: '“너희는 먼저 그의 나라와 그의 의를 구하라 그리하면 이 모든 것을 너희에게 더하시리라.”',
          options: ['베드로', '마태', '요한'],
          answer: '마태',
          talent: 5,
        },
        {
          level: 3,
          question: '“모든 것을 할 수 있는 그리스도 안에서 내게 능력 주시는 자 안에서 내가 모든 것을 할 수 있느니라.”',
          options: ['빌립보서 4:13', '로마서 8:28', '요한복음 3:16'],
          answer: '빌립보서 4:13',
          talent: 7,
        },
      ];
    };

    // 퀴즈 시작
    const startQuiz = async () => {
      quizStarted.value = true;
      await fetchQuestions();
      startTimer();
      startProgressBar();
    };

    // 타이머 시작
    const startTimer = () => {
      timer.value = 15;
      if (timerInterval.value) clearInterval(timerInterval.value);
      timerInterval.value = setInterval(() => {
        if (timer.value > 0) {
          timer.value--;
        } else {
          clearInterval(timerInterval.value);
          handleTimeOut();
        }
      }, 1000);
    };

    // 프로그레스바 시작
    const startProgressBar = () => {
      progressBarWidth.value = 100;
      if (progressInterval.value) clearInterval(progressInterval.value);
      progressInterval.value = setInterval(() => {
        if (progressBarWidth.value > 0) {
          progressBarWidth.value -= (100 / 15) / 10; // 15초 동안 부드럽게 줄어들도록
        } else {
          progressBarWidth.value = 0;
          clearInterval(progressInterval.value);
        }
      }, 100);
    };

    // 답안 선택
    const selectAnswer = (selectedOption) => {
      if (isAnswering.value) return;
      isAnswering.value = true;
      clearInterval(timerInterval.value);
      clearInterval(progressInterval.value);
      const current = currentQuestion.value;
      if (selectedOption === current.answer) {
        score.value += current.talent;
        isCorrect.value = true;
      } else {
        isCorrect.value = false;
      }
      showPopup.value = true;
    };

    // 시간 초과 처리
    const handleTimeOut = () => {
      isCorrect.value = false;
      showPopup.value = true;
    };

    // 팝업 닫기 및 다음 질문으로 이동
    const closePopup = () => {
      showPopup.value = false;
      isAnswering.value = false;
      if (currentQuestionIndex.value < questions.value.length - 1) {
        currentQuestionIndex.value++;
        startTimer();
        startProgressBar();
      } else {
        quizCompleted.value = true;
      }
    };

    // 퀴즈 리셋
    const resetQuiz = () => {
      quizStarted.value = false;
      quizCompleted.value = false;
      questions.value = [];
      currentQuestionIndex.value = 0;
      timer.value = 15;
      score.value = 0;
      showPopup.value = false;
      isCorrect.value = false;
      progressBarWidth.value = 100;
    };

    onMounted(() => {
      // 초기화 작업 (필요시 추가)
    });

    return {
      quizStarted,
      quizCompleted,
      questions,
      currentQuestionIndex,
      timer,
      score,
      showPopup,
      isCorrect,
      isAnswering,
      startQuiz,
      selectAnswer,
      closePopup,
      resetQuiz,
      currentQuestion,
      progressBarWidth,
    };
  },
};
</script>

<style>
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
