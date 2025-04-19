import { useState, useCallback } from 'react';

const useLoading = (initialState = false) => {
  const [isLoading, setIsLoading] = useState(initialState);
  const [error, setError] = useState(null);

  const startLoading = useCallback(() => {
    setIsLoading(true);
    setError(null);
  }, []);

  const stopLoading = useCallback(() => {
    setIsLoading(false);
  }, []);

  const setLoadingError = useCallback((error) => {
    setError(error);
    setIsLoading(false);
  }, []);

  const withLoading = useCallback(async (asyncFunction) => {
    try {
      startLoading();
      const result = await asyncFunction();
      return result;
    } catch (error) {
      setLoadingError(error);
      throw error;
    } finally {
      stopLoading();
    }
  }, [startLoading, stopLoading, setLoadingError]);

  return {
    isLoading,
    error,
    startLoading,
    stopLoading,
    setLoadingError,
    withLoading
  };
};

export default useLoading; 