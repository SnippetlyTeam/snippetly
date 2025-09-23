import styles from './MainButton.module.scss';

import React from 'react';

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  content: string;
};

const MainButton: React.FC<Props> = ({ content, ...rest }) => (
  <button className={`${styles.button} buttonText`} {...rest}>
    {content}
  </button>
);

export default MainButton;