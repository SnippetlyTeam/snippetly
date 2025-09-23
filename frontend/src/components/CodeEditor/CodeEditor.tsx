import styles from './CodeEditor.module.scss';
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { oneDark } from '@codemirror/theme-one-dark';
import { useState } from 'react';

const CodeEditor = () => {
  const [code, setCode] = useState([
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
  ].join('\n'));

  return (
    <div className={styles.editor}>
      <CodeMirror
        value={code}
        extensions={[javascript({ jsx: true })]}
        theme={oneDark}
        style={{
          maxHeight: '350px',
          overflowY: 'auto'
        }}
        onChange={setCode}
      />
    </div>
  );
};

export default CodeEditor;