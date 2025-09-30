import { createContext, useContext, useState, type ReactNode } from "react";

type AppStateType = {
  isAuthorized: boolean
}

type AppDispatchType = {
  setIsAuthorized: (prev: boolean) => void
}

const AppStateContext = createContext<AppStateType | null>(null);
const AppDispatchContext = createContext<AppDispatchType | null>(null);

type Props = {
  children: ReactNode;
}

export const AppProvider: React.FC<Props> = ({ children }) => {
  const [isAuthorized, setIsAuthorized] = useState(false);

  const stateValue = {
    isAuthorized
  }

  const dispatchValue = {
    setIsAuthorized
  }

  return (
    <AppStateContext.Provider value={stateValue}>
      <AppDispatchContext.Provider value={dispatchValue}>
        {children}
      </AppDispatchContext.Provider>
    </AppStateContext.Provider>
  )
}

export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error('useAppState must be used within an AppProvider');
  }
  return context;
};

export const useAppDispatch = () => {
  const context = useContext(AppDispatchContext);
  if (!context) {
    throw new Error('useAppDispatch must be used within an AppProvider');
  }
  return context;
};