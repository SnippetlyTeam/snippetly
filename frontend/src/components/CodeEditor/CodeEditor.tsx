import styles from './CodeEditor.module.scss';
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import type { SnippetLanguageType } from '../../types/SnippetLanguageType';

type Props = {
  language: SnippetLanguageType
  value?: string
  setValue?: (value: string) => void
}

const CodeEditor: React.FC<Props> = ({
  language,
  value = '',
  setValue = () => { },
}) => (
  <div className={styles.editor}>
    <CodeMirror
      value={value}
      extensions={
        language === 'js'
          ? [javascript({ jsx: true })]
          : [python()]
      }
      theme={oneDark}
      style={{
        maxHeight: '350px',
        overflowY: 'auto'
      }}
      onChange={setValue}
    />
  </div>
);

export default CodeEditor;