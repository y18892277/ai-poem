import { defineStore } from 'pinia';
import { ref } from 'vue';
import { startNewBattle, submitBattleAnswer, abortBattle } from '@/api/battle'; // Assuming @ refers to src
import { ElMessage } from 'element-plus';

export const useGameStore = defineStore('game', () => {
  const currentGame = ref(null); // Stores the full battle object from backend
  const currentQuestion = ref('');
  const gameMode = ref(''); // 'normal_chain' or 'smart_chain'
  const isLoading = ref(false);
  const feedbackMessage = ref('');
  const isCorrect = ref(null); // true, false, or null
  const gameOver = ref(false);
  const score = ref(0);

  async function startGame(type) {
    isLoading.value = true;
    feedbackMessage.value = '';
    isCorrect.value = null;
    gameOver.value = false;
    currentGame.value = null;
    currentQuestion.value = '';
    score.value = 0;
    gameMode.value = type;
    try {
      const response = await startNewBattle(type);
      currentGame.value = response; // Assuming API returns the battle object directly
      currentQuestion.value = response.current_question;
      score.value = response.score;
      ElMessage.success('新对战开始！');
    } catch (error) {
      console.error('Error starting game:', error);
      feedbackMessage.value = error.message || '开始对战失败';
      ElMessage.error(feedbackMessage.value);
      gameOver.value = true;
    } finally {
      isLoading.value = false;
    }
  }

  async function submitAnswer(answer) {
    if (!currentGame.value || !currentGame.value.id) {
      feedbackMessage.value = '没有进行中的对战信息！';
      ElMessage.error(feedbackMessage.value);
      return;
    }
    isLoading.value = true;
    feedbackMessage.value = '';
    isCorrect.value = null;
    try {
      const response = await submitBattleAnswer(currentGame.value.id, answer);
      currentGame.value = response.updated_battle_state;
      currentQuestion.value = response.updated_battle_state.current_question;
      score.value = response.updated_battle_state.score;
      isCorrect.value = response.is_correct;
      feedbackMessage.value = response.message;

      if (response.is_correct) {
        ElMessage.success(response.message || '回答正确！');
      } else {
        ElMessage.error(response.message || '回答错误！');
      }

      if (response.updated_battle_state.status !== 'active') {
        gameOver.value = true;
        currentQuestion.value = ''; // Clear question on game over
        ElMessage.info(response.updated_battle_state.status === 'completed_win' ? '恭喜获胜！' : '挑战失败！');
      }
      
    } catch (error) {
      console.error('Error submitting answer:', error);
      feedbackMessage.value = error.message || '提交答案失败';
      ElMessage.error(feedbackMessage.value);
    } finally {
      isLoading.value = false;
    }
  }

  function resetGame() {
    currentGame.value = null;
    currentQuestion.value = '';
    gameMode.value = '';
    isLoading.value = false;
    feedbackMessage.value = '';
    isCorrect.value = null;
    gameOver.value = false;
    score.value = 0;
  }

  async function exitGame() {
    if (!currentGame.value || !currentGame.value.id) {
      feedbackMessage.value = '没有可退出的对战。';
      ElMessage.info(feedbackMessage.value);
      return;
    }
    if (currentGame.value.status !== 'active'){
      feedbackMessage.value = '当前对战已结束或非活动状态，无需退出。';
      ElMessage.info(feedbackMessage.value);
      return;
    }

    isLoading.value = true;
    try {
      const response = await abortBattle(currentGame.value.id);
      currentGame.value = response; // Update with the aborted battle state
      currentQuestion.value = ''; // Clear question
      score.value = response.score; // Update score (might be unchanged or reset by backend)
      gameOver.value = true; // Mark game as over
      feedbackMessage.value = '对战已成功中止。';
      ElMessage.success(feedbackMessage.value);
    } catch (error) {
      console.error('Error exiting game:', error);
      feedbackMessage.value = error.message || '退出对战失败';
      ElMessage.error(feedbackMessage.value);
      // Depending on error, gameOver might not be set to true, 
      // or it might be set if server confirms it's already over.
    } finally {
      isLoading.value = false;
    }
  }

  return {
    currentGame,
    currentQuestion,
    gameMode,
    isLoading,
    feedbackMessage,
    isCorrect,
    gameOver,
    score,
    startGame,
    submitAnswer,
    resetGame,
    exitGame
  };
}); 