export default function CourseCard() {
  return (
    <div className="border border-gray-200 bg-white rounded-lg p-5 shadow-sm">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-xl font-bold text-black">FMS 001: Intro to Film</h3>
        <span className="bg-green-100 text-black text-sm font-bold px-3 py-1 rounded-full">
          94% Match
        </span>
      </div>
      <p className="text-black text-sm mb-4">
        <span className="font-semibold text-black">Why:</span> Satisfies your remaining Arts & Humanities GE.
      </p>
      <div className="flex gap-2">
        <span className="bg-gray-100 text-black text-xs px-2 py-1 rounded">4 Units</span>
      </div>
    </div>
  );
}