function BarGraph({data=[]}) {

    const maxCapacity = Math.max(...data.map(item => item.capacity))

    return (
        <div style={{ display: "flex", alignItems: "flex-end" }}>
            {data.map((item) =>(
                <div key={item.label} style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <div
                        className="bar"
                        style={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            height: `${(item.capacity / maxCapacity) * 300}px`,
                            width: `200px`,
                            margin: `8px`,
                            backgroundColor: "#ff8000"
                        }}
                    >
                        <span
                            style={{
                                fontSize: "14px",
                                marginBottom: "6px",
                                fontWeight: "500",
                            }}
                        >
                            {item.capacity}
                        </span>
                    </div>
                    <span>
                        {item.label}
                    </span>
                </div>
            ))}
        </div>
    )}

export default BarGraph











