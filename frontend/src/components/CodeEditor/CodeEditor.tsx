import styles from './CodeEditor.module.scss';
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';

type Props = {
  language: string
  value?: string
  onChange?: (value: string) => void
}

const CodeEditor: React.FC<Props> = ({
  language,
  value = '',
  onChange = () => { },
}) => (
  <div className={styles.editor}>
    <CodeMirror
      value={value}
      extensions={
        language === 'javascript'
          ? [javascript({ jsx: true })]
          : [python()]
      }
      theme={oneDark}
      style={{
        maxHeight: '350px',
        overflowY: 'auto'
      }}
      onChange={onChange}
    />
  </div>
);

export default CodeEditor;