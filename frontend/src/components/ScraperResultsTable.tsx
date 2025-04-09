// ScraperResultsTable.tsx
import React from 'react';
import './ScraperResultsTable.css';

interface Record {
  title: string;
  authors: string;
  article_url: string;
  pico: string | { [key: string]: string };
  pico_url: string;
  complete_review: string;
}

interface Props {
  records: Record[];
}

const ScraperResultsTable: React.FC<Props> = ({ records }) => {
  return (
    <div className="scraper-results-table">
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Authors</th>
            <th>Article URL</th>
            <th>PICO</th>
            <th>PICO URL</th>
            <th>Review Excerpt</th>
          </tr>
        </thead>
        <tbody>
          {records.map((rec, idx) => (
            <tr key={idx}>
              <td>{rec.title}</td>
              <td>{rec.authors}</td>
              <td>
                <a href={rec.article_url} target="_blank" rel="noreferrer">
                  Link
                </a>
              </td>
              <td>
                {typeof rec.pico === 'object'
                  ? Object.values(rec.pico).join(', ')
                  : rec.pico}
              </td>
              <td>
                {rec.pico_url !== 'N/A' ? (
                  <a href={rec.pico_url} target="_blank" rel="noreferrer">
                    Link
                  </a>
                ) : (
                  'N/A'
                )}
              </td>
              <td>{rec.complete_review.substring(0, 150)}...</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ScraperResultsTable;
