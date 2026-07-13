import React from 'react';

export default function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-thumb skeleton"></div>
      <div className="skeleton-body">
        <div className="skeleton-title skeleton"></div>
        <div className="skeleton-text skeleton"></div>
        <div className="skeleton-price skeleton"></div>
      </div>
    </div>
  );
}
