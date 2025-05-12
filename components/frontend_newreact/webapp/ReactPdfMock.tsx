import React from 'react';

const Document = ({ children }) => <div>{children}</div>;
const Page = () => <div>Page</div>;
const pdfjs = {
  GlobalWorkerOptions: {
    workerSrc: '',
  },
};

export { Document, Page, pdfjs };
export default { Document, Page };