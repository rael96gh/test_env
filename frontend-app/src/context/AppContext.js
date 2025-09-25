/**
 * Global application context
 */
import React, { createContext, useContext, useReducer, useCallback } from 'react';

// Initial state
const initialState = {
  user: null,
  theme: 'light',
  notifications: [],
  currentSequence: null,
  generatedOligos: [],
  lastResults: null,
};

// Action types
export const ACTIONS = {
  SET_USER: 'SET_USER',
  SET_THEME: 'SET_THEME',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  SET_CURRENT_SEQUENCE: 'SET_CURRENT_SEQUENCE',
  SET_GENERATED_OLIGOS: 'SET_GENERATED_OLIGOS',
  SET_LAST_RESULTS: 'SET_LAST_RESULTS',
  CLEAR_RESULTS: 'CLEAR_RESULTS',
};

// Reducer
const appReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.SET_USER:
      return { ...state, user: action.payload };

    case ACTIONS.SET_THEME:
      return { ...state, theme: action.payload };

    case ACTIONS.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [...state.notifications, { id: Date.now(), ...action.payload }],
      };

    case ACTIONS.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload),
      };

    case ACTIONS.SET_CURRENT_SEQUENCE:
      return { ...state, currentSequence: action.payload };

    case ACTIONS.SET_GENERATED_OLIGOS:
      return { ...state, generatedOligos: action.payload };

    case ACTIONS.SET_LAST_RESULTS:
      return { ...state, lastResults: action.payload };

    case ACTIONS.CLEAR_RESULTS:
      return {
        ...state,
        generatedOligos: [],
        lastResults: null,
        currentSequence: null,
      };

    default:
      return state;
  }
};

// Context
const AppContext = createContext();

// Provider component
export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Action creators
  const setUser = useCallback((user) => {
    dispatch({ type: ACTIONS.SET_USER, payload: user });
  }, []);

  const setTheme = useCallback((theme) => {
    dispatch({ type: ACTIONS.SET_THEME, payload: theme });
  }, []);

  const addNotification = useCallback((notification) => {
    dispatch({ type: ACTIONS.ADD_NOTIFICATION, payload: notification });

    // Auto-remove after 5 seconds for non-persistent notifications
    if (!notification.persistent) {
      setTimeout(() => {
        dispatch({ type: ACTIONS.REMOVE_NOTIFICATION, payload: notification.id || Date.now() });
      }, 5000);
    }
  }, []);

  const removeNotification = useCallback((id) => {
    dispatch({ type: ACTIONS.REMOVE_NOTIFICATION, payload: id });
  }, []);

  const setCurrentSequence = useCallback((sequence) => {
    dispatch({ type: ACTIONS.SET_CURRENT_SEQUENCE, payload: sequence });
  }, []);

  const setGeneratedOligos = useCallback((oligos) => {
    dispatch({ type: ACTIONS.SET_GENERATED_OLIGOS, payload: oligos });
  }, []);

  const setLastResults = useCallback((results) => {
    dispatch({ type: ACTIONS.SET_LAST_RESULTS, payload: results });
  }, []);

  const clearResults = useCallback(() => {
    dispatch({ type: ACTIONS.CLEAR_RESULTS });
  }, []);

  const value = {
    ...state,
    setUser,
    setTheme,
    addNotification,
    removeNotification,
    setCurrentSequence,
    setGeneratedOligos,
    setLastResults,
    clearResults,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

// Hook to use the context
export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export default AppContext;