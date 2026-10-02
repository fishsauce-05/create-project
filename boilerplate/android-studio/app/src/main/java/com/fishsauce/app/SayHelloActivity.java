package com.fishsauce.app;

import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.TextView;

public class SayHelloActivity {
    private final Handler handler = new Handler(Looper.getMainLooper());

    public void start(TextView txtHello, TextView txtHelp) {
        String hello = txtHello.getText().toString();
        txtHello.setText("");

        txtHelp.setVisibility(View.INVISIBLE);

        for (int i = 0; i < hello.length(); i++) {
            final int index = i;

            handler.postDelayed(() -> {
                txtHello.append(String.valueOf(hello.charAt(index)));

                if (index == hello.length() - 1) {
                    handler.postDelayed(() -> {
                        txtHelp.setVisibility(View.VISIBLE);
                    }, 500);
                }
            }, index * 80L);
        }
    }

    public void cancel() {
        handler.removeCallbacksAndMessages(null);
    }
}