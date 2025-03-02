@app.on_event("shutdown")
async def cleanup():
    """🔥 Cleanup separator to prevent semaphore leaks on shutdown."""
    global separator
    print("Shutting down, cleaning up Spleeter resources...")

    try:
        # Manually clean up TensorFlow session and multiprocessing pool
        if hasattr(separator, "_session"):
            separator._session.close()  # Close TensorFlow session
        if hasattr(separator, "_pool"):
            separator._pool.close()  # Close multiprocessing pool
            separator._pool.join()   # Ensure all processes are cleaned up
        
        del separator  # 🔥 Dereference the object for garbage collection
    except Exception as e:
        print("Error while deleting separator:", e)
