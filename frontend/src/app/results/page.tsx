'use client';

import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Suspense, useEffect, useState } from 'react';

type CourseCardProps = {
  title: string;
  matchPercentage: string | number;
  explanation: string;
  units: string | number;
};

function CourseCard({ title, matchPercentage, explanation, units }: CourseCardProps) {
  return (
    <article className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
      <div className="flex justify-between items-start gap-4">
        <h4 className="text-lg font-bold text-[#022851]">{title}</h4>
        <span className="shrink-0 text-sm font-semibold text-[#022851] bg-[#B3A369]/10 px-3 py-1 rounded-full">
          {matchPercentage} match
        </span>
      </div>
      <p className="mt-3 text-gray-600">{explanation}</p>
      <p className="mt-3 text-sm font-medium text-gray-500">Units: {units}</p>
    </article>
  );
}

function ResultsData() {
  const searchParams = useSearchParams();
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // 1. Extract parameters directly
  const interests = searchParams.get('interests') || '';
  const ge = searchParams.get('ge') || 'Any';
  const units = searchParams.get('units') || 'Any';
  const major = searchParams.get('major') || 'Any';
  const completed = searchParams.get('completed') || '';

useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        // 1. Dynamically build the payload. Only add optional fields if they are actually used.
        // Change these variable names on the left (ge, units, major) if Lulu used different ones!
        const payload: Record<string, any> = {
          interests: [interests]
        };

        if (ge !== 'Any') payload.ge = ge;
        if (units !== 'Any') payload.units = parseInt(units, 10);
        if (major !== 'Any') payload.major = major;
        if (completed.trim() !== '') payload.completed = completed;

        const response = await fetch('http://localhost:8000/recommend/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => null);
          // 2. This will force the exact FastAPI error to print as readable text in your console
          console.error("FastAPI Error Details:", JSON.stringify(errorData, null, 2));
          throw new Error(`Backend rejected request with status: ${response.status}`);
        }

        const data = await response.json();
        setRecommendations(data); 
      } catch (error) {
        console.error('Error fetching recommendations:', error);
      } finally {
        setIsLoading(false);
      }
    };

    if (interests) {
      fetchRecommendations();
    } else {
      setIsLoading(false);
    }
  }, [interests, ge, units, major, completed]);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-2 bg-[#B3A369]"></div>
        <h2 className="text-2xl font-bold text-[#022851] mb-6 border-b pb-4">
          Searching for: "{interests}"
        </h2>
        
        <div className="flex gap-3">
          <span className="bg-[#B3A369]/10 text-[#022851] px-3 py-1 rounded-full text-sm font-semibold border border-[#B3A369]/20">
            GE: {ge}
          </span>
          <span className="bg-[#B3A369]/10 text-[#022851] px-3 py-1 rounded-full text-sm font-semibold border border-[#B3A369]/20">
            Units: {units}
          </span>
          <span className="bg-blue-50 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold border border-blue-100">
            Major: {major}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-xl font-bold text-gray-800">Top Matches</h3>
        
        {isLoading ? (
          <div className="text-center py-10 text-gray-500 animate-pulse">
            AggieAI is analyzing the catalog...
          </div>
        ) : recommendations.length > 0 ? (
          recommendations.map((course, index) => (
            <CourseCard 
              key={index}
              title={course.title || "Course Title"} 
              matchPercentage={course.match_score || "90%"} 
              explanation={course.explanation || "Matches your interests."}
              units={course.units || units}
            />
          ))
        ) : (
          <div className="text-center py-10 text-gray-500">
            No courses found matching those exact criteria.
          </div>
        )}
      </div>

      <div className="mt-8">
        <Link href="/" className="inline-block text-[#B3A369] font-bold hover:text-[#022851] transition-colors">
          ← Start a New Search
        </Link>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto mt-6">
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-extrabold text-[#022851] tracking-tight mb-2">AggieAI</h1>
        </header>
        
        <Suspense fallback={<div className="text-center text-gray-500 font-medium mt-20 animate-pulse">Loading profile data...</div>}>
          <ResultsData />
        </Suspense>
      </div>
    </main>
  );
}