import styles from './MainButton.module.scss';

import React from 'react';

type Props = {
  content: React.ReactNode;
  [key: string]: any;
};

const MainButton: React.FC<Props> = ({ content, ...rest }) => (
  <button className={`${styles.button} buttonText`} {...rest}>
    {content}
  </button>
);

export default MainButton;