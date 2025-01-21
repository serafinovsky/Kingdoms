export default function NotFound() {
  return (
    <div class="min-h-screen flex items-center justify-center bg-gray-100">
      <div class="text-center">
        <h1 class="text-6xl font-bold text-gray-800 mb-4">404</h1>
        <p class="text-xl text-gray-600 mb-5">Oops! This page does not exist</p>
        <a
          href="/"
          class="inline-block px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-lg transition duration-300 ease-in-out"
        >
          Go to Homepage
        </a>
      </div>
    </div>
  );
};
