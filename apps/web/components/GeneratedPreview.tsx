"use client";
import { Sandpack } from "@codesandbox/sandpack-react";

export function GeneratedPreview({ code }: { code: string }) {
  const files: Record<string, string> = {
    "/App.tsx": code,
    "/index.tsx": `import React from 'react';\nimport { createRoot } from 'react-dom/client';\nimport App from './App';\nconst root = createRoot(document.getElementById('root')!);\nroot.render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>\n);\n`,
    "/index.html": `<!doctype html>\n<html>\n  <head>\n    <meta charset='UTF-8'/>\n    <meta name='viewport' content='width=device-width, initial-scale=1'/>\n    <title>Preview</title>\n    <script src='https://cdn.tailwindcss.com'></script>\n  </head>\n  <body>\n    <div id='root'></div>\n  </body>\n</html>`
  };

  return (
    <Sandpack
      template="react-ts"
      files={files}
      options={{
        showConsole: true,
        showTabs: true,
        editorHeight: 400,
        editorWidthPercentage: 50,
        externalResources: []
      }}
    />
  );
}