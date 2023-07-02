package net.techet.netanalyzershared.net;

import java.io.Serializable;
import java.net.InetAddress;
import java.net.UnknownHostException;
import o.kg0;
/* loaded from: classes.dex */
public class PingValue implements Serializable {
    public boolean i;
    public InetAddress j;
    public double k;
    public boolean l;

    public PingValue(boolean z, byte[] bArr, double d, int i, boolean z2) {
        this.i = z;
        this.k = d;
        this.l = z2;
        if (bArr != null) {
            try {
                this.j = InetAddress.getByAddress(bArr);
            } catch (UnknownHostException e) {
                kg0.a(e, true);
            }
        }
    }

    public PingValue(boolean z, InetAddress inetAddress, double d, int i) {
        this.i = z;
        this.j = inetAddress;
        this.k = d;
        this.l = false;
    }
}
