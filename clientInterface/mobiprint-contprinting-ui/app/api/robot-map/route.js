export async function GET() {
  try {
    const response = await fetch(
      'http://192.168.2.29/api/v2/robot/state/map',
      {
        cache: 'no-store', // important for real-time data
      }
    );

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: 'Failed to fetch robot map' }),
        { status: response.status }
      );
    }

    const data = await response.json();

    return Response.json(data);
  } catch (error) {
    return new Response(
      JSON.stringify({ error: 'Server error', details: error.message }),
      { status: 500 }
    );
  }
}