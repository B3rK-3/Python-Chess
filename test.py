import asyncio
async def test_stockfish():
    stockfish = await asyncio.create_subprocess_exec(
        "stockfish.exe",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    # 1. Tell Stockfish to go into UCI mode
    stockfish.stdin.write(b"uci\n")
    await stockfish.stdin.drain()
    
    # 2. Wait for 'uciok'
    while True:
        line = await asyncio.wait_for(stockfish.stdout.readline(), timeout=5)
        decoded = line.decode("utf-8").strip()
        print(decoded)
        if decoded == "uciok":
            break
    
    # 3. Send 'isready'
    stockfish.stdin.write(b"isready\n")
    await stockfish.stdin.drain()
    
    # 4. Wait for 'readyok'
    while True:
        line = await asyncio.wait_for(stockfish.stdout.readline(), timeout=5)
        decoded = line.decode("utf-8").strip()
        print(decoded)
        if decoded == "readyok":
            break
    
    # 5. Optionally 'ucinewgame'
    stockfish.stdin.write(b"ucinewgame\n")
    await stockfish.stdin.drain()
    
    # 6. Send position (startpos as an example)
    #    For FEN you might do: 
    #    b"position fen rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 1 2\n"
    stockfish.stdin.write(b"position fen r3k2r/ppppppPp/8/2q5/8/8/PPPPP1PP/R1P1K2R w kq - 0 1\n")
    await stockfish.stdin.drain()
    
    # 7. Send 'go movetime 1000' command
    stockfish.stdin.write(b"go movetime 1000\n")
    await stockfish.stdin.drain()
    
    # 8. Capture the engine’s output until we get 'bestmove'
    while True:
        line = await asyncio.wait_for(stockfish.stdout.readline(), timeout=10)
        decoded = line.decode("utf-8").strip()
        print(decoded)
        if decoded.startswith("bestmove"):
            print("Best move received:", decoded)
            break
    
    # Cleanup
    stockfish.terminate()
    await stockfish.wait()

asyncio.run(test_stockfish())
