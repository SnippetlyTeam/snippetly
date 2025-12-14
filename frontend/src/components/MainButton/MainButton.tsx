import styles from './MainButton.module.scss';

import React from 'react';

type Props = {
  content: React.ReactNode;
  disabled?: boolean;
  [key: string]: any;
};

const MainButton: React.FC<Props> = ({ content, disabled = false, ...rest }) => (
  <button 
    className={`${styles.button} buttonText`} 
    {...rest}
    disabled={disabled}
  >
    {content}
  </button>
);

export default MainButton;