export default function LoadingSpinner() {
  return (
    <div class="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div class="w-24 h-24 border-4 border-blue-500 border-solid rounded-full border-t-transparent animate-spin"></div>
    </div>
  );
}
