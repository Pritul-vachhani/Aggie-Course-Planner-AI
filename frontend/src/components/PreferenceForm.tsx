'use client';

export default function PreferenceForm() {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-lg font-bold text-gray-800 mb-4">Find Your Class</h2>
      <form className="space-y-4">
        <div>
          <label className="block text-sm text-gray-700 mb-1">What are your interests?</label>
          <textarea className="w-full border border-gray-300 rounded-md p-3 min-h-[100px]" />
        </div>
        <button type="button" className="w-full bg-blue-800 text-white font-semibold py-3 rounded-md">
          Search Courses
        </button>
      </form>
    </div>
  );
}