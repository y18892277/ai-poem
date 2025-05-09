<template>
  <div class="battle-page">
    <h1>诗词接龙</h1>
    
    <div v-if="!gameStore.currentGame && !gameStore.gameOver">
      <h2>选择模式开始对战</h2>
      <el-button type="primary" @click="startGameMode('normal_chain')" :loading="gameStore.isLoading">常规接龙</el-button>
      <el-button type="success" @click="startGameMode('smart_chain')" :loading="gameStore.isLoading">智能接龙</el-button>
    </div>

    <div v-if="gameStore.currentGame">
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>对战模式: {{ gameStore.gameMode === 'normal_chain' ? '常规接龙' : '智能接龙' }}</span>
            <span>分数: {{ gameStore.score }}</span>
          </div>
        </template>
        
        <div v-if="!gameStore.gameOver">
          <p class="question">题目：{{ gameStore.currentQuestion }}</p>
          <el-input 
            v-model="userAnswer"
            placeholder="请输入你的答案"
            :disabled="gameStore.isLoading"
            @keyup.enter="handleSubmitAnswer"
          />
          <el-button 
            type="primary" 
            @click="handleSubmitAnswer" 
            :loading="gameStore.isLoading"
            style="margin-top: 10px;"
            >提交答案</el-button>
          
          <el-button 
            type="danger" 
            @click="handleExitGame" 
            :loading="gameStore.isLoading"
            v-if="gameStore.currentGame && !gameStore.gameOver && gameStore.currentGame.status === 'active'"
            style="margin-top: 10px; margin-left: 10px;"
            plain
            >退出游戏</el-button>
        </div>

        <div v-if="gameStore.feedbackMessage" class="feedback-message"
             :class="{'correct': gameStore.isCorrect === true, 'incorrect': gameStore.isCorrect === false}">
          <p>{{ gameStore.feedbackMessage }}</p>
        </div>

        <div v-if="gameStore.gameOver">
          <h2>对战结束!</h2>
          <p>最终得分: {{ gameStore.score }}</p>
          <el-button @click="handlePlayAgain">再来一局</el-button>
        </div>
      </el-card>
    </div>

  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue';
import { useGameStore } from '@/store/game'; // Adjust path if necessary
import { ElMessage } from 'element-plus'; // For direct use if needed, though store handles some

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
  if (gameStore.isCorrect) { // If correct and game not over, clear for next answer
    if (!gameStore.gameOver) {
        userAnswer.value = '';
    }
  } 
  // If incorrect, user might want to see their answer, so don't clear automatically
  // Or clear if game over
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
.battle-page {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  text-align: center;
}
.box-card {
  margin-top: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.question {
  font-size: 1.2em;
  margin-bottom: 15px;
  white-space: pre-wrap; /* To respect newlines in question if any */
}
.feedback-message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
}
.feedback-message.correct {
  color: #67c23a;
  background-color: #f0f9eb;
  border: 1px solid #e1f3d8;
}
.feedback-message.incorrect {
  color: #f56c6c;
  background-color: #fef0f0;
  border: 1px solid #fde2e2;
}
</style> 