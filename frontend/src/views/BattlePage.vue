<template>
  <div class="battle-page-container">
    <el-card class="main-card" shadow="hover">
      <template #header>
        <div class="main-card-header">
          <h1>诗词接龙挑战</h1>
        </div>
      </template>

      <div v-if="!gameStore.currentGame && !gameStore.gameOver" class="mode-selection">
        <h2>选择模式开始对战</h2>
        <div class="mode-buttons">
          <el-button size="large" type="primary" @click="startGameMode('normal_chain')" :loading="gameStore.isLoading">常规接龙</el-button>
          <el-button size="large" type="success" @click="startGameMode('smart_chain')" :loading="gameStore.isLoading">智能接龙</el-button>
        </div>
      </div>

      <div v-if="gameStore.currentGame" class="battle-active-area">
        <el-card class="game-status-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>模式: {{ gameStore.gameMode === 'normal_chain' ? '常规接龙' : '智能接龙' }}</span>
              <span class="score">当前分数: {{ gameStore.score }}</span>
            </div>
          </template>
          
          <div v-loading="gameStore.isLoading" element-loading-text="处理中...">
            <div v-if="!gameStore.gameOver" class="game-interaction">
              <p class="question-display">题目：<strong>{{ gameStore.currentQuestion }}</strong></p>
              <el-input 
                v-model="userAnswer"
                placeholder="请输入你的答案"
                :disabled="gameStore.isLoading"
                @keyup.enter="handleSubmitAnswer"
                size="large"
                clearable
              />
              <div class="action-buttons">
                <el-button 
                  type="primary" 
                  @click="handleSubmitAnswer" 
                  :loading="gameStore.isLoading"
                  size="large"
                  >提交答案</el-button>
                <el-button 
                  type="info" 
                  @click="handleExitGame" 
                  :loading="gameStore.isLoading"
                  v-if="gameStore.currentGame && !gameStore.gameOver && gameStore.currentGame.status === 'active'"
                  size="large"
                  plain
                  >退出游戏</el-button>
              </div>
            </div>

            <div v-if="gameStore.feedbackMessage && !gameStore.gameOver" class="feedback-container">
                <el-alert
                    :title="gameStore.feedbackMessage"
                    :type="gameStore.isCorrect === true ? 'success' : (gameStore.isCorrect === false ? 'error' : 'info')"
                    :closable="false"
                    show-icon
                    class="feedback-alert"
                />
            </div>

            <div v-if="gameStore.gameOver" class="game-over-section">
              <el-result
                :icon="gameStore.currentGame.status === 'completed_win' || gameStore.currentGame.status === 'aborted' ? 'success' : 'error'"
                :title="gameStore.currentGame.status === 'aborted' ? '对战已中止' : (gameStore.currentGame.status === 'completed_win' ? '恭喜获胜!' : '挑战失败!')"
                :sub-title="`最终得分: ${gameStore.score}`"
              >
                <template #extra>
                  <el-button type="primary" size="large" @click="handlePlayAgain">再来一局</el-button>
                </template>
              </el-result>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue';
import { useGameStore } from '@/store/game'; // Adjust path if necessary
import { ElMessage, ElAlert, ElResult } from 'element-plus'; // Added ElAlert, ElResult if not already there

const gameStore = useGameStore();
const userAnswer = ref('');

async function startGameMode(mode) {
  await gameStore.startGame(mode);
  userAnswer.value = ''; // Clear previous answer
}

async function handleSubmitAnswer() {
  if (!userAnswer.value.trim()) {
    ElMessage.warning('请输入答案！');
    return;
  }
  await gameStore.submitAnswer(userAnswer.value.trim());
  if (gameStore.isCorrect && !gameStore.gameOver) { 
    userAnswer.value = '';
  } 
  if (gameStore.gameOver) {
      userAnswer.value = '';
  }
}

function handlePlayAgain() {
  gameStore.resetGame(); 
  // UI will revert to mode selection
}

// Reset game store when component is unmounted if desired
onUnmounted(() => {
  // gameStore.resetGame(); // Optional: reset if user navigates away mid-game
});

function handleExitGame() {
  gameStore.exitGame();
}

</script>

<style scoped>
.battle-page-container {
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Align to top for better view on smaller heights */
  min-height: calc(100vh - 100px); /* Adjust based on your nav/footer height */
  padding: 20px;
  background-color: #fdfaf6; /* Changed to a warmer, paper-like off-white */
  transition: background-color 0.3s ease; /* Smooth transition for background color changes */
}

.main-card {
  width: 100%;
  max-width: 700px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12); /* Slightly adjusted shadow for more depth */
  background-color: #fff; /* Explicitly set card background to white */
}

.main-card-header h1 {
  text-align: center;
  color: #303133; /* Darker title */
  font-size: 2em; /* Larger title */
  margin-bottom: 0; /* Remove bottom margin from h1 inside header */
}

.mode-selection {
  text-align: center;
  padding: 30px 0;
}

.mode-selection h2 {
  margin-bottom: 25px;
  color: #606266;
}

.mode-buttons .el-button {
  margin: 0 10px;
  padding: 15px 30px; /* Larger buttons */
  font-size: 1.1em;
}

.battle-active-area {
  margin-top: 10px;
}

.game-status-card {
  border: none; /* Remove border from inner card */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1em;
  color: #409EFF; /* Theme color for status */
}
.card-header .score {
  font-weight: bold;
}

.game-interaction {
  padding: 20px;
  text-align: center;
}

.question-display {
  font-size: 1.5em; /* Larger question text */
  color: #303133;
  margin-bottom: 25px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.question-display strong {
 color: #409EFF;
}

.el-input {
  margin-bottom: 20px;
}

.action-buttons .el-button {
  margin: 10px 5px 0;
}

.feedback-container {
    margin: 20px;
    min-height: 60px; /* Ensure space even if message is short or not present yet */
}

.feedback-alert {
    text-align: left; /* Align alert text to left for better readability */
}

.game-over-section {
  padding: 20px;
  text-align: center;
}

.game-over-section .el-result {
    padding: 20px 0; /* Adjust padding for result component */
}

.game-over-section h2 {
  font-size: 1.8em;
  margin-bottom: 10px;
  color: #303133;
}

.game-over-section p {
  font-size: 1.2em;
  margin-bottom: 20px;
  color: #606266;
}
</style> 