import React from 'react';

const FormattedResponse = ({ text }) => {
  const formatText = (text) => {
    if (!text) return '';
    
    // Convert markdown-like syntax to HTML
    let formatted = text
      // Handle line breaks
      .replace(/\n/g, '<br>')
      
      // Handle headers
      .replace(/### (.*?)(<br>|$)/g, '<h3>$1</h3>')
      .replace(/## (.*?)(<br>|$)/g, '<h2>$1</h2>')
      .replace(/# (.*?)(<br>|$)/g, '<h1>$1</h1>')
      
      // Handle bold text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      
      // Handle bullet points
      .replace(/^- (.*?)(<br>|$)/gm, '<li>$1</li>')
      
      // Handle numbered lists
      .replace(/^\d+\. (.*?)(<br>|$)/gm, '<li>$1</li>')
      
      // Wrap consecutive list items in ul tags
      .replace(/(<li>.*?<\/li>)(<br>)?(?=<li>)/g, '$1')
      .replace(/(<li>.*?<\/li>)(<br>)*(?!<li>)/g, '<ul>$1</ul>')
      
      // Handle emphasis
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      
      // Handle code blocks
      .replace(/`(.*?)`/g, '<code>$1</code>')
      
      // Clean up extra breaks
      .replace(/<br><br>/g, '<br>')
      .replace(/<br>(<h[1-6])/g, '$1')
      .replace(/(<\/h[1-6]>)<br>/g, '$1')
      
      // Handle paragraphs
      .split('<br>')
      .map(line => {
        line = line.trim();
        if (!line) return '';
        if (line.match(/^<[h1-6ul\/]/)) return line;
        if (line.match(/^<li>/)) return line;
        return `<p>${line}</p>`;
      })
      .join('');
    
    return formatted;
  };

  return (
    <div 
      className="response-text"
      dangerouslySetInnerHTML={{ __html: formatText(text) }}
    />
  );
};

export default FormattedResponse;