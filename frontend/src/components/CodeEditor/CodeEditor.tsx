import styles from './CodeEditor.module.scss';
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { oneDark } from '@codemirror/theme-one-dark';

const CodeEditor = () => {
  const code = [
    '// Save and share your favorite code snippets!',
    'function saveSnippet(snippet) {',
    '  if (!snippet) {',
    '    console.log("Oops! No snippet to save.");',
    '    return;',
    '  }',
    '  console.log(`Snippet saved: "${snippet}"`);',
    '}',
    '',
    "saveSnippet(\"console.log('Hello, snippets!');\");"
  ].join('\n');

  return (
    <div
      className={styles.editor}
    >
      <CodeMirror
        value={code}
        extensions={[javascript({ jsx: true })]}
        theme={oneDark}
        style={{
          maxHeight: '350px',
          overflowY: 'auto'
        }}
      />
    </div>
  );
};

export default CodeEditor;