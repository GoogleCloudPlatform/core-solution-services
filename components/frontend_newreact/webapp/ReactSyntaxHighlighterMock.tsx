import React from 'react';

const ReactSyntaxHighlighterMock = ({ children }) => {
  return <pre>{children}</pre>; // Simple mock that just renders children
};

export const Prism = ReactSyntaxHighlighterMock;
export default ReactSyntaxHighlighterMock;